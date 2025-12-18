# diagnostic_chroma.py
import os
import chromadb
from chromadb.config import Settings

# Make path absolute, same as your vector_store
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
VECTOR_DB_PATH = os.path.join(BASE_DIR, "data", "vector_db")

print("Chroma vector DB path:", VECTOR_DB_PATH)

# Initialize Chroma client
client = chromadb.Client(
    Settings(
        persist_directory=VECTOR_DB_PATH,
        anonymized_telemetry=False
    )
)

# List all collections
collections = client.list_collections()
print(f"Collections found: {len(collections)}")
for c in collections:
    print("-", c.name)

# Peek into first collection if exists
if collections:
    col = collections[0]
    peek = col.peek()
    print("Keys in collection peek:", peek.keys())
    if peek.get("documents"):
        print("Sample document:", peek["documents"][0][:200])
    else:
        print("No documents in collection")
else:
    print("No collections present at all")
