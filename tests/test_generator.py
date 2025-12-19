# tests/test_generator.py

import pytest
from src.generation.generator import Generator

# ========================================
# FIXTURES
# ========================================

@pytest.fixture
def generator():
    """Create a generator instance for testing"""
    return Generator(model_name="llama3.1:8b")


@pytest.fixture
def sample_contexts():
    """Sample context data for various test scenarios"""
    return {
        "library_hours": [
            "The university library is open from 8 AM to 8 PM on weekdays.",
            "On weekends, the library operates from 9 AM to 5 PM.",
            "During exam weeks, the library extends hours to 10 PM."
        ],
        "admission": [
            "Applications for undergraduate programs open on January 15th.",
            "The admission test will be held on March 10th at the main campus.",
            "Required documents: 10+2 marksheet, ID proof, and passport-size photos."
        ],
        "facilities": [
            "The campus has a gymnasium, swimming pool, and sports complex.",
            "Medical facilities are available 24/7 at the health center.",
            "Free Wi-Fi is available across the entire campus."
        ],
        "partial_info": [
            "The computer lab is located in Block C."
            # Missing: lab timings, access requirements
        ],
        "irrelevant": [
            "The university was founded in 1985.",
            "The campus covers 100 acres of land."
        ]
    }


# ========================================
# TEST CATEGORY 1: NORMAL OPERATIONS
# ========================================

def test_normal_query_with_full_context(generator, sample_contexts):
    """Test: Generator answers correctly when full context is available"""
    query = "What are the library working hours?"
    answer = generator.generate(query, sample_contexts["library_hours"])
    
    # Should contain key information
    assert "8 AM" in answer or "8AM" in answer
    assert "weekday" in answer.lower() or "monday" in answer.lower()
    assert len(answer) > 20  # Non-trivial response


def test_specific_detail_extraction(generator, sample_contexts):
    """Test: Generator extracts specific details accurately"""
    query = "When is the admission test?"
    answer = generator.generate(query, sample_contexts["admission"])
    
    assert "march" in answer.lower() or "10" in answer
    assert "10th" in answer.lower() or "march 10" in answer.lower()


def test_list_based_query(generator, sample_contexts):
    """Test: Generator handles queries requiring list of items"""
    query = "What facilities are available on campus?"
    answer = generator.generate(query, sample_contexts["facilities"])
    
    # Should mention at least 2 facilities
    facilities_mentioned = sum([
        "gymnasium" in answer.lower() or "gym" in answer.lower(),
        "swimming" in answer.lower() or "pool" in answer.lower(),
        "medical" in answer.lower() or "health" in answer.lower(),
        "wi-fi" in answer.lower() or "wifi" in answer.lower()
    ])
    
    assert facilities_mentioned >= 2


# ========================================
# TEST CATEGORY 2: HALLUCINATION PREVENTION
# ========================================

def test_empty_context_refusal(generator):
    """Test: Generator refuses to answer when context is empty"""
    query = "What are the hostel rules?"
    answer = generator.generate(query, [])
    
    # Should contain refusal language
    refusal_keywords = ["don't have", "not available", "cannot answer", "knowledge base"]
    assert any(keyword in answer.lower() for keyword in refusal_keywords)


def test_out_of_scope_query_refusal(generator, sample_contexts):
    """Test: Generator refuses when context doesn't contain answer"""
    query = "What is the hostel curfew time?"
    # Context is about library, not hostel
    answer = generator.generate(query, sample_contexts["library_hours"])
    
    # Should refuse or indicate lack of information
    refusal_indicators = ["don't have", "not found", "cannot answer", "not available"]
    assert any(indicator in answer.lower() for indicator in refusal_indicators)


def test_fabrication_prevention(generator, sample_contexts):
    """Test: Generator doesn't fabricate specific details (phone numbers, dates)"""
    query = "What is the library contact number?"
    # Context doesn't have phone number
    answer = generator.generate(query, sample_contexts["library_hours"])
    
    # Should NOT contain fabricated phone numbers
    # Common patterns: +91, (xxx) xxx-xxxx, etc.
    assert "+91" not in answer
    assert "phone" not in answer.lower() or "don't have" in answer.lower()


def test_partial_context_handling(generator, sample_contexts):
    """Test: Generator acknowledges when context is incomplete"""
    query = "What are the computer lab timings and access requirements?"
    answer = generator.generate(query, sample_contexts["partial_info"])
    
    # Should indicate partial information or refuse
    partial_indicators = [
        "based on available",
        "don't have",
        "partial",
        "not specified",
        "cannot answer"
    ]
    assert any(indicator in answer.lower() for indicator in partial_indicators)


# ========================================
# TEST CATEGORY 3: EDGE CASES
# ========================================

def test_ambiguous_query(generator, sample_contexts):
    """Test: Generator handles ambiguous queries appropriately"""
    query = "What are the hours?"  # Ambiguous: hours of what?
    answer = generator.generate(query, sample_contexts["library_hours"])
    
    # Should either ask for clarification or provide available info
    assert len(answer) > 10  # Should not be empty


def test_whitespace_only_context(generator):
    """Test: Generator handles whitespace-only context"""
    query = "What are the admission requirements?"
    answer = generator.generate(query, ["   ", "\n\n", "\t\t"])
    
    refusal_keywords = ["don't have", "not available"]
    assert any(keyword in answer.lower() for keyword in refusal_keywords)


def test_very_long_context(generator):
    """Test: Generator handles very long context without crashing"""
    query = "What facilities are available?"
    long_context = ["Facility information: " + "A" * 5000]  # Very long context
    
    try:
        answer = generator.generate(query, long_context)
        assert isinstance(answer, str)
        assert len(answer) > 0
    except Exception as e:
        pytest.fail(f"Generator crashed with long context: {e}")


def test_special_characters_in_query(generator, sample_contexts):
    """Test: Generator handles special characters gracefully"""
    query = "What's the library's timing? (weekdays only!)"
    answer = generator.generate(query, sample_contexts["library_hours"])
    
    assert isinstance(answer, str)
    assert len(answer) > 0


def test_multiple_questions_in_one(generator, sample_contexts):
    """Test: Generator handles compound queries"""
    query = "What are the library hours and what facilities does it have?"
    combined_context = sample_contexts["library_hours"] + sample_contexts["facilities"]
    answer = generator.generate(query, combined_context)
    
    # Should attempt to answer both parts
    assert "library" in answer.lower()
    assert len(answer) > 30


# ========================================
# TEST CATEGORY 4: ERROR HANDLING
# ========================================

def test_none_context(generator):
    """Test: Generator handles None context gracefully"""
    query = "What are the admission dates?"
    answer = generator.generate(query, None)
    
    # Should not crash, should refuse
    assert isinstance(answer, str)
    assert len(answer) > 0


def test_invalid_model_name():
    """Test: Generator with invalid model name handles errors"""
    generator = Generator(model_name="nonexistent-model-xyz")
    answer = generator.generate("Test query", ["Test context"])
    
    # Should return error message, not crash
    assert isinstance(answer, str)
    assert "error" in answer.lower() or "not available" in answer.lower()


# ========================================
# TEST CATEGORY 5: SAFETY & QUALITY
# ========================================

def test_no_external_knowledge_leak(generator):
    """Test: Generator doesn't use knowledge outside provided context"""
    query = "Who is the current Prime Minister of India?"
    # Context deliberately has wrong info
    fake_context = ["The current Prime Minister is John Doe."]
    
    answer = generator.generate(query, fake_context)
    
    # Should use context info (John Doe), not real-world knowledge
    # OR refuse if recognizing context-query mismatch
    assert "john doe" in answer.lower() or "don't have" in answer.lower()


def test_consistent_refusal_format(generator):
    """Test: Refusal messages follow consistent format"""
    queries = [
        "What is the weather?",
        "Tell me a joke",
        "What's the hostel wifi password?"
    ]
    
    refusals = [generator.generate(q, []) for q in queries]
    
    # All should refuse with similar language
    for refusal in refusals:
        assert "don't have" in refusal.lower() or "not available" in refusal.lower()


# ========================================
# HALLUCINATION TEST SCENARIOS (DOCUMENTATION)
# ========================================

HALLUCINATION_TEST_CASES = """
=== HALLUCINATION PREVENTION TEST SCENARIOS ===

SCENARIO 1: Complete Information Absence
Query: "What is the hostel fee structure?"
Context: [Library hours, admission dates]
Expected: Refusal - "I don't have that information..."

SCENARIO 2: Partial Information (Missing Critical Details)
Query: "How do I apply for admission and what are the fees?"
Context: [Application opens on Jan 15th] (NO fee information)
Expected: Either (a) Answer only application part + note missing fees, OR (b) Full refusal

SCENARIO 3: Fabrication of Specifics
Query: "What is the library contact number?"
Context: [Library hours, location] (NO phone number)
Expected: Refusal - must NOT generate fake numbers like +91-XXXXXXXXXX

SCENARIO 4: Temporal Inference
Query: "Is the library open right now?"
Context: [Library hours: 8 AM - 8 PM weekdays]
Expected: Provide hours, do NOT infer current day/time

SCENARIO 5: Cross-Domain Confusion
Query: "Where is the computer lab?"
Context: [Admission process details]
Expected: Refusal - completely different domain

SCENARIO 6: Ambiguity Exploitation
Query: "When does it open?"
Context: [Library hours, admission dates, gym timings]
Expected: Ask for clarification OR provide all "opening times"

SCENARIO 7: Leading Questions
Query: "The hostel curfew is 10 PM, right?"
Context: [No hostel information]
Expected: Refuse - do NOT confirm false assumption

SCENARIO 8: Impossible Requests
Query: "Predict the cutoff for next year's admission"
Context: [Past year admission data]
Expected: Refuse - cannot predict future
"""


# ========================================
# RUN INSTRUCTIONS
# ========================================

if __name__ == "__main__":
    print("Running SAGE Generator Test Suite...")
    print("\nTo run tests:")
    print("  pytest tests/test_generator.py -v")
    print("\nTo run specific test:")
    print("  pytest tests/test_generator.py::test_empty_context_refusal -v")
    print("\nTo see hallucination test scenarios:")
    print(HALLUCINATION_TEST_CASES)