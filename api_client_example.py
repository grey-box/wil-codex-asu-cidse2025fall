"""
API Client Example
Shows how to use the parameter validation API
"""

import requests
import json
from typing import Dict, Any


class TranslationAPIClient:
    """Client for the translation API with built-in validation"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
    
    def translate(
        self,
        text: str,
        content_type: str,
        language_origin: str = "en",
        translated_language: str = "es",
        confidence_threshold: float = 0.8
    ) -> Dict[str, Any]:
        """
        Translate text from one language to another
        
        Args:
            text: Text to translate
            content_type: Type of content ('prescription' or 'symptom')
            language_origin: Source language code (default: 'en')
            translated_language: Target language code (default: 'es')
            confidence_threshold: Minimum confidence score (default: 0.8)
        
        Returns:
            Translation result dictionary
        """
        payload = {
            "type": content_type,
            "text": text,
            "language_origin": language_origin,
            "translated_language": translated_language,
            "confidence_threshold": confidence_threshold
        }
        
        response = requests.post(
            f"{self.base_url}/translate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            raise Exception(f"API Error: {error_data.get('message', 'Unknown error')}")
    
    def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        sort_by: str = "relevance"
    ) -> Dict[str, Any]:
        """
        Search for content
        
        Args:
            query: Search query
            limit: Maximum number of results (default: 10)
            offset: Number of results to skip (default: 0)
            sort_by: Sort order ('relevance', 'date', or 'popularity')
        
        Returns:
            Search results dictionary
        """
        params = {
            "query": query,
            "limit": limit,
            "offset": offset,
            "sort_by": sort_by
        }
        
        response = requests.get(f"{self.base_url}/search", params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            raise Exception(f"API Error: {error_data.get('message', 'Unknown error')}")


def demo_successful_calls():
    """Demonstrate successful API calls"""
    print("=" * 70)
    print("✅ SUCCESSFUL API CALLS")
    print("=" * 70)
    
    client = TranslationAPIClient()
    
    # Example 1: Basic translation
    print("\n1. Basic Translation (English to Spanish)")
    print("-" * 70)
    try:
        result = client.translate(
            text="Take two tablets with water after meals",
            content_type="prescription",
            language_origin="en",
            translated_language="es"
        )
        print("✓ Success!")
        print(f"Input: {result['input']['text']}")
        print(f"Translation: {result['output']['translated_text']}")
        print(f"Confidence: {result['output']['confidence']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Example 2: Using defaults
    print("\n2. Translation with Default Values")
    print("-" * 70)
    try:
        result = client.translate(
            text="Patient reports severe headache",
            content_type="symptom"
        )
        print("✓ Success!")
        print(f"Used defaults: {result['input']['from']} → {result['input']['to']}")
        print(f"Confidence threshold: {result['output']['meets_threshold']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Example 3: Search
    print("\n3. Search Query")
    print("-" * 70)
    try:
        result = client.search(
            query="medical symptoms",
            limit=5,
            sort_by="date"
        )
        print("✓ Success!")
        print(f"Query: {result['query']}")
        print(f"Results: {len(result['results'])}")
        print(f"Total available: {result['pagination']['total_results']}")
    except Exception as e:
        print(f"✗ Error: {e}")


def demo_validation_errors():
    """Demonstrate validation error handling"""
    print("\n\n" + "=" * 70)
    print("❌ VALIDATION ERROR HANDLING")
    print("=" * 70)
    
    client = TranslationAPIClient()
    
    # Example 1: Missing required parameter
    print("\n1. Missing Required Parameter")
    print("-" * 70)
    try:
        response = requests.post(
            "http://localhost:5000/translate",
            json={
                "language_origin": "en",
                "translated_language": "es"
                # Missing: type and text
            }
        )
        data = response.json()
        print(f"Status Code: {response.status_code}")
        print(f"Error: {data['error']}")
        print(f"Message:\n{data['message']}")
    except Exception as e:
        print(f"Request Error: {e}")
    
    # Example 2: Invalid value for constrained parameter
    print("\n2. Invalid Content Type")
    print("-" * 70)
    try:
        response = requests.post(
            "http://localhost:5000/translate",
            json={
                "type": "diagnosis",  # Not in allowed values
                "text": "Patient has fever",
                "language_origin": "en",
                "translated_language": "es"
            }
        )
        data = response.json()
        print(f"Status Code: {response.status_code}")
        print(f"Error: {data['error']}")
        print(f"Message:\n{data['message']}")
    except Exception as e:
        print(f"Request Error: {e}")
    
    # Example 3: Invalid language code format
    print("\n3. Invalid Language Code Format")
    print("-" * 70)
    try:
        response = requests.post(
            "http://localhost:5000/translate",
            json={
                "type": "prescription",
                "text": "Take medicine",
                "language_origin": "eng",  # Should be 2 letters
                "translated_language": "es"
            }
        )
        data = response.json()
        print(f"Status Code: {response.status_code}")
        print(f"Error: {data['error']}")
        print(f"Message:\n{data['message']}")
    except Exception as e:
        print(f"Request Error: {e}")
    
    # Example 4: Text too long
    print("\n4. Text Length Violation")
    print("-" * 70)
    try:
        response = requests.post(
            "http://localhost:5000/translate",
            json={
                "type": "prescription",
                "text": "a" * 6000,  # Exceeds max_length of 5000
                "language_origin": "en",
                "translated_language": "es"
            }
        )
        data = response.json()
        print(f"Status Code: {response.status_code}")
        print(f"Error: {data['error']}")
        print(f"Message:\n{data['message']}")
    except Exception as e:
        print(f"Request Error: {e}")
    
    # Example 5: Invalid confidence threshold
    print("\n5. Confidence Threshold Out of Range")
    print("-" * 70)
    try:
        response = requests.post(
            "http://localhost:5000/translate",
            json={
                "type": "symptom",
                "text": "Headache",
                "confidence_threshold": 1.5  # Should be between 0 and 1
            }
        )
        data = response.json()
        print(f"Status Code: {response.status_code}")
        print(f"Error: {data['error']}")
        print(f"Message:\n{data['message']}")
    except Exception as e:
        print(f"Request Error: {e}")


def demo_pagination():
    """Demonstrate pagination with search"""
    print("\n\n" + "=" * 70)
    print("📄 PAGINATION EXAMPLE")
    print("=" * 70)
    
    client = TranslationAPIClient()
    
    print("\nFetching search results in pages...")
    
    for page in range(3):
        offset = page * 5
        print(f"\n--- Page {page + 1} (offset: {offset}) ---")
        
        try:
            result = client.search(
                query="medical terms",
                limit=5,
                offset=offset
            )
            
            for item in result['results']:
                print(f"  • {item['title']}")
            
            print(f"\nShowing {len(result['results'])} of {result['pagination']['total_results']} total results")
            
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🔧 PARAMETER VALIDATION API - CLIENT DEMO")
    print("=" * 70)
    print("\nMake sure the Flask API server is running first!")
    print("Start it with: python flask_api_example.py")
    print("\nPress Enter to continue with the demo...")
    input()
    
    try:
        # Test connection
        response = requests.get("http://localhost:5000/")
        if response.status_code == 200:
            print("✓ Connected to API server\n")
        
        # Run demos
        demo_successful_calls()
        demo_validation_errors()
        demo_pagination()
        
        print("\n" + "=" * 70)
        print("✅ DEMO COMPLETE")
        print("=" * 70)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API server")
        print("Please start the server first with: python flask_api_example.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
