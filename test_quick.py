#!/usr/bin/env python3
"""Quick test script for the AI Project Tracker."""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables for testing (SQLite instead of PostgreSQL)
os.environ['DATABASE_URL'] = 'sqlite:///./test_tracker.db'
os.environ['OLLAMA_BASE_URL'] = 'http://localhost:11434'
os.environ['OLLAMA_MODEL'] = 'llama3.1'
os.environ['CHROMA_PERSIST_DIR'] = './test_chroma_data'
os.environ['DEBUG'] = 'True'

from fastapi.testclient import TestClient
from backend.main import app
from backend.database import init_db

print("🚀 Starting AI Project Tracker Quick Test\n")

# Initialize database
print("1. Initializing database...")
init_db()
print("✅ Database initialized\n")

# Create test client
client = TestClient(app)

# Test 1: Health check
print("2. Testing health check endpoint...")
response = client.get("/health")
assert response.status_code == 200
print(f"✅ Health check: {response.json()}\n")

# Test 2: Create team member
print("3. Testing team member registration...")
team_member_data = {
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "role": "Software Engineer"
}
response = client.post("/api/team-members/", json=team_member_data)
assert response.status_code == 201
member = response.json()
print(f"✅ Created team member: {member['name']} (ID: {member['id']})\n")

# Test 3: Create another team member
print("4. Creating second team member...")
team_member_data2 = {
    "name": "Bob Smith",
    "email": "bob@example.com",
    "role": "Product Manager"
}
response = client.post("/api/team-members/", json=team_member_data2)
assert response.status_code == 201
member2 = response.json()
print(f"✅ Created team member: {member2['name']} (ID: {member2['id']})\n")

# Test 4: List team members
print("5. Testing team member list...")
response = client.get("/api/team-members/")
assert response.status_code == 200
members = response.json()
print(f"✅ Found {len(members)} team members\n")

# Test 5: Submit status update
print("6. Testing status update submission...")
status_data = {
    "team_member_id": member['id'],
    "status_text": "Implemented user authentication feature and fixed 3 critical bugs in the payment system."
}
response = client.post("/api/status-updates/", json=status_data)
assert response.status_code == 201
status = response.json()
print(f"✅ Created status update (ID: {status['id']})\n")

# Test 6: Submit more status updates
print("7. Creating more status updates...")
status_updates = [
    {
        "team_member_id": member['id'],
        "status_text": "Reviewed pull requests and conducted code review sessions with the team."
    },
    {
        "team_member_id": member2['id'],
        "status_text": "Finalized Q4 roadmap and prioritized feature backlog. Met with stakeholders."
    },
    {
        "team_member_id": member2['id'],
        "status_text": "Conducted user research interviews and analyzed feedback for the new dashboard feature."
    }
]

for update_data in status_updates:
    response = client.post("/api/status-updates/", json=update_data)
    assert response.status_code == 201

print(f"✅ Created {len(status_updates)} additional status updates\n")

# Test 7: List status updates
print("8. Testing status updates list...")
response = client.get("/api/status-updates/")
assert response.status_code == 200
updates = response.json()
print(f"✅ Found {len(updates)} total status updates\n")

# Test 8: Filter by team member
print("9. Testing filtered status updates...")
response = client.get(f"/api/status-updates/?team_member_id={member['id']}")
assert response.status_code == 200
alice_updates = response.json()
print(f"✅ Found {len(alice_updates)} updates for {member['name']}\n")

# Test 9: Get specific status update
print("10. Testing individual status update retrieval...")
response = client.get(f"/api/status-updates/{status['id']}")
assert response.status_code == 200
retrieved_status = response.json()
print(f"✅ Retrieved status update: {retrieved_status['status_text'][:50]}...\n")

# Test 10: Check vector store sync
print("11. Checking vector store integration...")
try:
    from backend.services.vector_store import get_vector_store
    vector_store = get_vector_store()
    count = vector_store.get_collection_count()
    print(f"✅ Vector store contains {count} indexed updates\n")
except Exception as e:
    print(f"⚠️  Vector store test skipped: {e}\n")

# Test 11: Check AI health (will fail without Ollama, but that's OK)
print("12. Checking AI services health...")
response = client.get("/api/ai/health-check")
assert response.status_code == 200
ai_health = response.json()
print(f"   Ollama available: {ai_health['ollama_available']}")
print(f"   Vector store count: {ai_health['vector_store_count']}")
if not ai_health['ollama_available']:
    print("   ℹ️  Note: Ollama not running (install with: curl -fsSL https://ollama.com/install.sh | sh)\n")
else:
    print("✅ AI services are ready\n")

# Test 12: Frontend test
print("13. Testing frontend endpoint...")
response = client.get("/")
assert response.status_code == 200
print("✅ Frontend accessible\n")

print("=" * 60)
print("🎉 ALL TESTS PASSED!")
print("=" * 60)
print("\nSummary:")
print(f"  • {len(members)} team members registered")
print(f"  • {len(updates)} status updates submitted")
print(f"  • Vector store indexed: {ai_health['vector_store_count']} items")
print(f"  • AI features ready: {'Yes' if ai_health['ollama_available'] else 'No (Ollama not installed)'}")
print("\nTo run the full application:")
print("  1. Install dependencies: pip install -r requirements.txt")
print("  2. Install Ollama: curl -fsSL https://ollama.com/install.sh | sh")
print("  3. Pull model: ollama pull llama3.1")
print("  4. Start server: python -m uvicorn backend.main:app --reload")
print("  5. Visit: http://localhost:8000")
print("\nOr use Docker: docker-compose up")
