"""
Flask API with Parameter Validation
A practical example of using the parameter validator in a REST API
"""

from flask import Flask, request, jsonify
from parameter_validator import (
    ParameterValidator, 
    ParameterDefinition, 
    ParameterType, 
    ValidationError
)
from functools import wraps
from typing import Dict, Any


app = Flask(__name__)


# Decorator for parameter validation
def validate_params(validator: ParameterValidator):
    """
    Decorator to automatically validate request parameters
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                # Get parameters from request (JSON body or query params)
                if request.is_json:
                    params = request.get_json()
                else:
                    params = request.args.to_dict()
                
                # Validate
                validated_params = validator.validate(params)
                
                # Pass validated params to the route function
                return f(validated_params, *args, **kwargs)
                
            except ValidationError as e:
                return jsonify({
                    "error": "Validation Error",
                    "message": str(e),
                    "status": 400
                }), 400
            except Exception as e:
                return jsonify({
                    "error": "Internal Server Error",
                    "message": str(e),
                    "status": 500
                }), 500
        
        return wrapper
    return decorator


# Create validator for translation endpoint
translation_validator = ParameterValidator()

translation_validator.add_parameter(ParameterDefinition(
    name="type",
    param_type=ParameterType.STRING,
    description="Type of content being translated",
    required=True,
    allowed_values=["prescription", "symptom"],
))

translation_validator.add_parameter(ParameterDefinition(
    name="language_origin",
    param_type=ParameterType.STRING,
    description="Source language code",
    required=False,
    default="en",
    pattern=r"^[a-z]{2}$"
))

translation_validator.add_parameter(ParameterDefinition(
    name="translated_language",
    param_type=ParameterType.STRING,
    description="Target language code",
    required=False,
    default="en",
    pattern=r"^[a-z]{2}$"
))

translation_validator.add_parameter(ParameterDefinition(
    name="text",
    param_type=ParameterType.STRING,
    description="Text to translate",
    required=True,
    min_length=1,
    max_length=5000
))

translation_validator.add_parameter(ParameterDefinition(
    name="confidence_threshold",
    param_type=ParameterType.FLOAT,
    description="Minimum confidence score",
    required=False,
    default=0.8,
    min_value=0.0,
    max_value=1.0
))


# Create validator for search endpoint
search_validator = ParameterValidator()

search_validator.add_parameter(ParameterDefinition(
    name="query",
    param_type=ParameterType.STRING,
    description="Search query",
    required=True,
    min_length=1,
    max_length=200
))

search_validator.add_parameter(ParameterDefinition(
    name="limit",
    param_type=ParameterType.INTEGER,
    description="Maximum results to return",
    required=False,
    default=10,
    min_value=1,
    max_value=100
))

search_validator.add_parameter(ParameterDefinition(
    name="offset",
    param_type=ParameterType.INTEGER,
    description="Number of results to skip",
    required=False,
    default=0,
    min_value=0
))

search_validator.add_parameter(ParameterDefinition(
    name="sort_by",
    param_type=ParameterType.STRING,
    description="Field to sort by",
    required=False,
    default="relevance",
    allowed_values=["relevance", "date", "popularity"]
))


# Routes
@app.route("/")
def home():
    """API home page"""
    return jsonify({
        "message": "Parameter Validation API",
        "version": "1.0",
        "endpoints": {
            "/translate": "POST - Translate text between languages",
            "/search": "GET - Search for content",
            "/docs/translate": "GET - Translation parameter documentation",
            "/docs/search": "GET - Search parameter documentation"
        }
    })


@app.route("/translate", methods=["POST"])
@validate_params(translation_validator)
def translate(params: Dict[str, Any]):
    """
    Translate text from one language to another
    
    This is a mock implementation - in production, you'd call a real translation service
    """
    
    # Mock translation logic
    result = {
        "success": True,
        "input": {
            "type": params["type"],
            "text": params["text"],
            "from": params["language_origin"],
            "to": params["translated_language"]
        },
        "output": {
            "translated_text": f"[TRANSLATED: {params['text']}]",
            "confidence": 0.95,
            "meets_threshold": 0.95 >= params["confidence_threshold"]
        },
        "metadata": {
            "engine": "mock-translator-v1",
            "processing_time_ms": 42
        }
    }
    
    return jsonify(result), 200


@app.route("/search", methods=["GET"])
@validate_params(search_validator)
def search(params: Dict[str, Any]):
    """
    Search for content with pagination and sorting
    
    This is a mock implementation
    """
    
    # Mock search results
    results = []
    for i in range(params["offset"], params["offset"] + params["limit"]):
        results.append({
            "id": i + 1,
            "title": f"Result {i + 1} for '{params['query']}'",
            "relevance_score": 0.9 - (i * 0.05),
            "date": "2025-01-15"
        })
    
    return jsonify({
        "success": True,
        "query": params["query"],
        "pagination": {
            "limit": params["limit"],
            "offset": params["offset"],
            "total_results": 87,
            "has_more": True
        },
        "sort_by": params["sort_by"],
        "results": results
    }), 200


@app.route("/docs/translate", methods=["GET"])
def translate_docs():
    """Get parameter documentation for translate endpoint"""
    docs = translation_validator.generate_documentation()
    return f"<pre>{docs}</pre>", 200, {"Content-Type": "text/html"}


@app.route("/docs/search", methods=["GET"])
def search_docs():
    """Get parameter documentation for search endpoint"""
    docs = search_validator.generate_documentation()
    return f"<pre>{docs}</pre>", 200, {"Content-Type": "text/html"}


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        "error": "Not Found",
        "message": "The requested endpoint does not exist",
        "status": 404
    }), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({
        "error": "Internal Server Error",
        "message": str(e),
        "status": 500
    }), 500


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Starting Parameter Validation API Server")
    print("=" * 60)
    print("\nEndpoints:")
    print("  • http://localhost:5000/")
    print("  • http://localhost:5000/translate (POST)")
    print("  • http://localhost:5000/search (GET)")
    print("  • http://localhost:5000/docs/translate")
    print("  • http://localhost:5000/docs/search")
    print("\n" + "=" * 60 + "\n")
    
    app.run(debug=True, host="0.0.0.0", port=5000)
