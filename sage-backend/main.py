"""
SAGE University Chatbot - Production Backend
Comprehensive error handling for real-world deployment
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
import logging
import sys
import os
from datetime import datetime
import traceback
import re
import asyncio
from contextlib import asynccontextmanager
import time

# Add project root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from src.pipeline.rag_graph import run_rag
from src.config import AVAILABLE_MODELS, DEFAULT_MODEL

# Logging configuration
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/backend.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Application state tracking
app_state = {
    "startup_time": None,
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "vector_db_loaded": False,
    "ollama_available": False,
    "average_response_time": 0,
    "request_times": []
}

# User-friendly error messages (no internal details exposed)
FRIENDLY_ERRORS = {
    "empty_question": "Please enter a question to continue.",
    "too_short": "Your question seems too brief. Could you provide more details?",
    "too_long": "Your question is quite long. Please try to be more concise.",
    "invalid_chars": "Your question contains invalid characters. Please use standard text.",
    "service_unavailable": "I'm currently unable to process requests. Please try again in a moment.",
    "timeout": "This is taking longer than expected. Please try asking a simpler question.",
    "processing_error": "I encountered an issue processing your question. Please try rephrasing it.",
    "no_answer": "I couldn't find relevant information to answer your question. Please try asking differently or contact the university administration.",
    "rate_limit": "You're asking questions too quickly. Please wait a moment before trying again.",
    "maintenance": "I'm currently undergoing maintenance. Please try again shortly."
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Startup
    logger.info("Starting SAGE Chatbot Backend")
    app_state["startup_time"] = datetime.now()
    
    # Verify dependencies silently (no user exposure)
    vector_db_path = os.path.join(BASE_DIR, "data", "vector_db")
    app_state["vector_db_loaded"] = os.path.exists(vector_db_path)
    
    import shutil
    app_state["ollama_available"] = shutil.which("ollama") is not None
    
    if app_state["vector_db_loaded"] and app_state["ollama_available"]:
        logger.info("All systems operational")
    else:
        logger.warning("System degraded - some components unavailable")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down - Processed {app_state['total_requests']} requests")

app = FastAPI(
    title="SAGE University Chatbot",
    description="Intelligent assistant for Pondicherry Technological University",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS - Allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permissive for all frontend configurations
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class ChatRequest(BaseModel):
    """Chat request with comprehensive validation"""
    question: str = Field(..., min_length=1, max_length=2000)
    
    @validator('question')
    def validate_question(cls, v):
        # Remove extra whitespace
        v = ' '.join(v.split())
        
        # Check if empty after cleanup
        if not v or len(v.strip()) == 0:
            raise ValueError(FRIENDLY_ERRORS["empty_question"])
        
        # Check minimum length
        if len(v.strip()) < 5:
            raise ValueError(FRIENDLY_ERRORS["too_short"])
        
        # Check for excessive length
        if len(v) > 1500:
            raise ValueError(FRIENDLY_ERRORS["too_long"])
        
        # Check for valid characters (allow common punctuation)
        if not re.match(r'^[a-zA-Z0-9\s\.\,\?\!\-\(\)\'\"\:\;\/\&\+\@\#\%]+$', v):
            # If contains some valid chars, strip invalid ones
            cleaned = re.sub(r'[^a-zA-Z0-9\s\.\,\?\!\-\(\)\'\"\:\;\/\&\+\@\#\%]', '', v)
            if len(cleaned.strip()) < 5:
                raise ValueError(FRIENDLY_ERRORS["invalid_chars"])
            v = cleaned
        
        return v.strip()

class ChatResponse(BaseModel):
    """Clean response to user - no internal details"""
    answer: str
    success: bool = True

class ErrorResponse(BaseModel):
    """User-friendly error response"""
    error: str
    success: bool = False

class HealthResponse(BaseModel):
    """System health status"""
    status: str
    available: bool

# Rate limiting (in-memory - simple but effective)
request_tracker: Dict[str, List[float]] = {}
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 30  # requests per window

def check_rate_limit(client_ip: str) -> bool:
    """Check if client has exceeded rate limit"""
    current_time = time.time()
    
    if client_ip not in request_tracker:
        request_tracker[client_ip] = []
    
    # Clean old requests
    request_tracker[client_ip] = [
        req_time for req_time in request_tracker[client_ip]
        if current_time - req_time < RATE_LIMIT_WINDOW
    ]
    
    # Check limit
    if len(request_tracker[client_ip]) >= RATE_LIMIT_MAX:
        return False
    
    # Add current request
    request_tracker[client_ip].append(current_time)
    return True

# Exception Handlers - Return only user-friendly messages
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with friendly messages"""
    app_state["failed_requests"] += 1
    
    errors = exc.errors()
    
    # Extract user-friendly message
    for error in errors:
        if "msg" in error and error["msg"]:
            # If it's our custom error message, use it
            if any(friendly_msg in str(error["msg"]) for friendly_msg in FRIENDLY_ERRORS.values()):
                error_msg = error["msg"]
                break
    else:
        error_msg = FRIENDLY_ERRORS["invalid_chars"]
    
    logger.warning(f"Validation error from {request.client.host}: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(error=error_msg).dict()
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with friendly messages"""
    app_state["failed_requests"] += 1
    
    logger.warning(f"HTTP {exc.status_code} from {request.client.host}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=exc.detail).dict()
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all exceptions - never expose internal errors to user"""
    app_state["failed_requests"] += 1
    
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(error=FRIENDLY_ERRORS["processing_error"]).dict()
    )

# Middleware for request tracking
@app.middleware("http")
async def track_requests(request: Request, call_next):
    """Track all requests and measure response time"""
    start_time = time.time()
    app_state["total_requests"] += 1
    
    response = await call_next(request)
    
    # Calculate response time
    response_time = (time.time() - start_time) * 1000  # Convert to ms
    
    # Update average response time
    app_state["request_times"].append(response_time)
    if len(app_state["request_times"]) > 100:  # Keep last 100
        app_state["request_times"].pop(0)
    app_state["average_response_time"] = sum(app_state["request_times"]) / len(app_state["request_times"])
    
    return response

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "SAGE University Chatbot",
        "status": "online",
        "message": "Welcome to PTU's AI Assistant"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Simple health check - no internal details"""
    is_healthy = app_state["vector_db_loaded"] and app_state["ollama_available"]
    
    return HealthResponse(
        status="online" if is_healthy else "limited",
        available=is_healthy
    )

@app.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest, req: Request):
    """
    Main chat endpoint - handles all user questions
    
    Edge cases handled:
    - Empty/whitespace questions
    - Very short questions (< 5 chars)
    - Very long questions (> 1500 chars)
    - Invalid/special characters
    - Rate limiting
    - System unavailability
    - RAG pipeline failures
    - Empty/invalid answers
    - Timeout scenarios
    - Network errors
    - Database errors
    - Model errors
    """
    
    client_ip = req.client.host
    start_time = time.time()
    
    try:
        # Rate limiting check
        if not check_rate_limit(client_ip):
            logger.warning(f"Rate limit exceeded for {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=FRIENDLY_ERRORS["rate_limit"]
            )
        
        # System availability check
        if not app_state["vector_db_loaded"]:
            logger.error("Vector database not available")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=FRIENDLY_ERRORS["service_unavailable"]
            )
        
        if not app_state["ollama_available"]:
            logger.error("Ollama not available")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=FRIENDLY_ERRORS["service_unavailable"]
            )
        
        # Log sanitized question (first 100 chars only)
        logger.info(f"Question from {client_ip}: {request.question[:100]}...")
        
        # Get model to use
        model_name = AVAILABLE_MODELS[DEFAULT_MODEL]["name"]
        
        # Run RAG pipeline with timeout protection
        try:
            # Execute RAG with asyncio timeout
            answer = await asyncio.wait_for(
                asyncio.to_thread(run_rag, request.question, model_name),
                timeout=60.0  # 60 second timeout
            )
        except asyncio.TimeoutError:
            logger.error(f"Timeout processing question from {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=FRIENDLY_ERRORS["timeout"]
            )
        except FileNotFoundError as e:
            logger.error(f"File not found in RAG pipeline: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=FRIENDLY_ERRORS["service_unavailable"]
            )
        except Exception as e:
            logger.error(f"RAG pipeline error: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=FRIENDLY_ERRORS["processing_error"]
            )
        
        # Validate answer
        if not answer or not answer.strip():
            logger.warning(f"Empty answer generated for question from {client_ip}")
            answer = FRIENDLY_ERRORS["no_answer"]
        
        # Clean answer - remove any internal error messages
        answer = answer.strip()
        
        # Check for common error patterns in answer and replace with friendly message
        error_patterns = [
            "error", "exception", "traceback", "failed", "unable to",
            "ollama", "vector", "database", "model", "timeout"
        ]
        
        answer_lower = answer.lower()
        if any(pattern in answer_lower for pattern in error_patterns):
            # If answer contains error indicators, check if it's a real error or just mentioning it
            if len(answer) < 100 or "i don't have" not in answer_lower:
                logger.warning("Answer contains error patterns - replacing")
                answer = FRIENDLY_ERRORS["no_answer"]
        
        # Ensure answer is substantial
        if len(answer.strip()) < 10:
            logger.warning("Answer too short - replacing")
            answer = FRIENDLY_ERRORS["no_answer"]
        
        # Track success
        app_state["successful_requests"] += 1
        processing_time = (time.time() - start_time) * 1000
        
        logger.info(f"Successfully answered question from {client_ip} in {processing_time:.0f}ms")
        
        return ChatResponse(
            answer=answer,
            success=True
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (already have friendly messages)
        raise
    except Exception as e:
        # Catch any unexpected errors - never expose to user
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=FRIENDLY_ERRORS["processing_error"]
        )

# Development server
if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("  SAGE University Chatbot Backend")
    print("  Starting on http://localhost:8000")
    print("=" * 60)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )