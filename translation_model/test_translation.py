"""
Test script for the translation service
"""
import requests
import json

BASE_URL = "http://localhost:8003"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_root():
    """Test root endpoint"""
    print("Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_translation(text):
    """Test translation endpoint"""
    print(f"Testing translation: '{text}'")
    
    payload = {
        "text": text,
        "source_lang": "en",
        "target_lang": "nl"
    }
    
    response = requests.post(
        f"{BASE_URL}/translate",
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Original:    {result['original_text']}")
        print(f"Translation: {result['translated_text']}\n")
    else:
        print(f"Error: {response.text}\n")

def main():
    print("="*60)
    print("Translation Service Test Script")
    print("="*60)
    print()
    
    try:
        # Test health
        test_health()
        
        # Test root
        test_root()
        
        # Test translations
        test_sentences = [
            "Hello, how are you today?",
            "The weather is beautiful.",
            "I love programming in Python.",
            "This is a test sentence.",
            "Good morning!",
            "Thank you very much for your help."
        ]
        
        print("="*60)
        print("Translation Tests")
        print("="*60)
        print()
        
        for sentence in test_sentences:
            test_translation(sentence)
        
        print("="*60)
        print("All tests completed!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the translation service.")
        print("Make sure the service is running on http://localhost:8003")
        print("\nTo start the service, run:")
        print("  python translation.py")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()
