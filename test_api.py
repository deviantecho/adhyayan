"""
Test script for NCERT RAG API
Run this after starting the API server with: python start_api.py
"""
import requests
import json

API_BASE = "http://127.0.0.1:8000"

def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{API_BASE}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_chat_non_streaming():
    """Test chat endpoint without streaming"""
    print("\n=== Testing Chat (Non-Streaming) ===")
    payload = {
        "message": "Explain chemical reactions.",
        "chat_history": [],
        "subject_filter": "All Subjects",
        "stream": False
    }

    response = requests.post(f"{API_BASE}/api/chat", json=payload)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Answer: {data['answer'][:200]}...")
        print(f"Sources: {len(data['sources'])} sources")
        print(f"Retrieval Details: {len(data['retrieval_details'])} chunks")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_chat_streaming():
    """Test chat endpoint with stream=True (SSE wrapper around the completed answer)"""
    print("\n=== Testing Chat (Streaming) ===")
    payload = {
        "message": "What are real numbers?",
        "chat_history": [],
        "subject_filter": "Mathematics",
        "stream": True
    }

    response = requests.post(
        f"{API_BASE}/api/chat",
        json=payload,
        stream=True
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        print("SSE response:")
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data = json.loads(line_str[6:])
                    if data['type'] == 'metadata':
                        print(f"  Sources: {len(data['sources'])}")
                    elif data['type'] == 'content':
                        # Single event containing the complete answer (not token-by-token)
                        print(f"  Complete answer ({len(data['content'])} chars): {data['content'][:50]}...")
                    elif data['type'] == 'done':
                        print(f"  Completed!")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_subject_filter():
    """Test subject filtering"""
    print("\n=== Testing Subject Filter ===")
    payload = {
        "message": "Explain triangles.",
        "chat_history": [],
        "subject_filter": "Mathematics",
        "stream": False
    }

    response = requests.post(f"{API_BASE}/api/chat", json=payload)

    if response.status_code == 200:
        data = response.json()
        print(f"Answer length: {len(data['answer'])} chars")
        print(f"All sources from Mathematics: {all('Mathematics' in s or 'Math' in s for s in data['sources'])}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_conversation_history():
    """Test conversation history"""
    print("\n=== Testing Conversation History ===")

    # First message
    payload1 = {
        "message": "What is photosynthesis?",
        "chat_history": [],
        "subject_filter": "Science",
        "stream": False
    }

    response1 = requests.post(f"{API_BASE}/api/chat", json=payload1)
    data1 = response1.json()

    # Follow-up using history
    payload2 = {
        "message": "Where does it occur?",
        "chat_history": data1['updated_history'],
        "subject_filter": "Science",
        "stream": False
    }

    response2 = requests.post(f"{API_BASE}/api/chat", json=payload2)

    if response2.status_code == 200:
        data2 = response2.json()
        print(f"Follow-up answer: {data2['answer'][:150]}...")
        print(f"History length: {len(data2['updated_history'])} messages")
        return True
    else:
        print(f"Error: {response2.text}")
        return False

def test_out_of_scope():
    """Test out-of-scope question"""
    print("\n=== Testing Out-of-Scope Question ===")
    payload = {
        "message": "What is quantum mechanics?",
        "chat_history": [],
        "subject_filter": "All Subjects",
        "stream": False
    }

    response = requests.post(f"{API_BASE}/api/chat", json=payload)

    if response.status_code == 200:
        data = response.json()
        print(f"Answer: {data['answer']}")
        print(f"No sources found: {len(data['sources']) == 0}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("NCERT RAG API Test Suite")
    print("=" * 50)

    tests = [
        ("Health Check", test_health),
        ("Chat Non-Streaming", test_chat_non_streaming),
        ("Chat Streaming", test_chat_streaming),
        ("Subject Filter", test_subject_filter),
        ("Conversation History", test_conversation_history),
        ("Out-of-Scope Question", test_out_of_scope)
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"Exception in {name}: {e}")
            results.append((name, False))

    print("\n" + "=" * 50)
    print("Test Results")
    print("=" * 50)
    for name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status}: {name}")

    passed = sum(1 for _, success in results if success)
    print(f"\nTotal: {passed}/{len(results)} tests passed")
