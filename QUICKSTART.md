# Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies
```bash
pip install flask requests pytest
```

### Step 2: Run the Demo
```bash
python parameter_validator.py
```

You'll see validation in action with different test cases!

### Step 3: Try the API (Optional)
```bash
# Terminal 1 - Start server
python flask_api_example.py

# Terminal 2 - Run client
python api_client_example.py
```

## Common Use Cases

### Use Case 1: Simple REST API Parameter Validation

**Problem**: You have a REST API and need to validate query parameters.

**Solution**:
```python
from parameter_validator import *

# Create validator
validator = ParameterValidator()

# Define parameters
validator.add_parameter(ParameterDefinition(
    name="search",
    param_type=ParameterType.STRING,
    description="Search query",
    required=True,
    min_length=2,
    max_length=100
))

validator.add_parameter(ParameterDefinition(
    name="limit",
    param_type=ParameterType.INTEGER,
    description="Max results",
    required=False,
    default=10,
    min_value=1,
    max_value=100
))

# Validate
try:
    params = validator.validate(request.args)
    results = search_database(params['search'], params['limit'])
except ValidationError as e:
    return {"error": str(e)}, 400
```

### Use Case 2: Form Data Validation

**Problem**: You need to validate user registration form data.

**Solution**:
```python
def is_strong_password(pwd):
    return (len(pwd) >= 8 and 
            any(c.isupper() for c in pwd) and 
            any(c.islower() for c in pwd) and 
            any(c.isdigit() for c in pwd))

validator = ParameterValidator()

validator.add_parameter(ParameterDefinition(
    name="username",
    param_type=ParameterType.STRING,
    description="Username",
    required=True,
    min_length=3,
    max_length=20,
    pattern=r"^[a-zA-Z0-9_]+$"
))

validator.add_parameter(ParameterDefinition(
    name="email",
    param_type=ParameterType.STRING,
    description="Email",
    required=True,
    pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$"
))

validator.add_parameter(ParameterDefinition(
    name="password",
    param_type=ParameterType.STRING,
    description="Password",
    required=True,
    min_length=8,
    custom_validator=is_strong_password,
    error_message="Password must contain uppercase, lowercase, and digits"
))

validator.add_parameter(ParameterDefinition(
    name="age",
    param_type=ParameterType.INTEGER,
    description="Age",
    required=True,
    min_value=13,
    max_value=120
))

# Use it
form_data = request.form.to_dict()
validated = validator.validate(form_data)
create_user(validated)
```

### Use Case 3: Configuration File Validation

**Problem**: You load config from JSON/YAML and need to validate it.

**Solution**:
```python
import json

validator = ParameterValidator()

validator.add_parameter(ParameterDefinition(
    name="database_url",
    param_type=ParameterType.STRING,
    description="Database connection string",
    required=True,
    pattern=r"^(postgresql|mysql):\/\/.+"
))

validator.add_parameter(ParameterDefinition(
    name="cache_ttl",
    param_type=ParameterType.INTEGER,
    description="Cache TTL in seconds",
    required=False,
    default=3600,
    min_value=0
))

validator.add_parameter(ParameterDefinition(
    name="debug_mode",
    param_type=ParameterType.BOOLEAN,
    description="Enable debug logging",
    required=False,
    default=False
))

# Load and validate
with open('config.json') as f:
    config = json.load(f)

validated_config = validator.validate(config)
initialize_app(validated_config)
```

### Use Case 4: Multi-Language Content API

**Problem**: You have a translation API and need to validate language codes and content.

**Solution** (from your image):
```python
validator = ParameterValidator()

# Content type (prescription or symptom)
validator.add_parameter(ParameterDefinition(
    name="type",
    param_type=ParameterType.STRING,
    description="Type of medical content",
    required=True,
    allowed_values=["prescription", "symptom"],
    error_message="Type must be 'prescription' or 'symptom'"
))

# Source language
validator.add_parameter(ParameterDefinition(
    name="language_origin",
    param_type=ParameterType.STRING,
    description="Source language (ISO 639-1)",
    required=False,
    default="en",
    pattern=r"^[a-z]{2}$",
    error_message="Language must be 2-letter ISO code (e.g., 'en', 'es')"
))

# Target language
validator.add_parameter(ParameterDefinition(
    name="translated_language",
    param_type=ParameterType.STRING,
    description="Target language (ISO 639-1)",
    required=False,
    default="en",
    pattern=r"^[a-z]{2}$",
    error_message="Language must be 2-letter ISO code"
))

# Text content
validator.add_parameter(ParameterDefinition(
    name="text",
    param_type=ParameterType.STRING,
    description="Text to translate",
    required=True,
    min_length=1,
    max_length=5000
))

# Quality threshold
validator.add_parameter(ParameterDefinition(
    name="confidence_threshold",
    param_type=ParameterType.FLOAT,
    description="Minimum translation confidence",
    required=False,
    default=0.8,
    min_value=0.0,
    max_value=1.0
))

# Use in API
@app.route('/translate', methods=['POST'])
def translate_endpoint():
    try:
        params = validator.validate(request.get_json())
        result = translate_text(
            params['text'],
            params['language_origin'],
            params['translated_language']
        )
        return jsonify(result)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
```

### Use Case 5: E-commerce Order Validation

**Problem**: Validate product orders with complex business rules.

**Solution**:
```python
def validate_product_sku(sku):
    """Custom: SKU must exist in database"""
    return product_exists(sku)

def validate_shipping_address(address):
    """Custom: Address must be deliverable"""
    return address.get('country') in SUPPORTED_COUNTRIES

validator = ParameterValidator()

validator.add_parameter(ParameterDefinition(
    name="product_sku",
    param_type=ParameterType.STRING,
    description="Product SKU",
    required=True,
    pattern=r"^[A-Z]{3}-\d{6}$",
    custom_validator=validate_product_sku,
    error_message="Invalid or non-existent product SKU"
))

validator.add_parameter(ParameterDefinition(
    name="quantity",
    param_type=ParameterType.INTEGER,
    description="Order quantity",
    required=True,
    min_value=1,
    max_value=999
))

validator.add_parameter(ParameterDefinition(
    name="shipping_address",
    param_type=ParameterType.DICT,
    description="Delivery address",
    required=True,
    custom_validator=validate_shipping_address,
    error_message="Invalid or unsupported shipping address"
))

validator.add_parameter(ParameterDefinition(
    name="coupon_code",
    param_type=ParameterType.STRING,
    description="Discount coupon",
    required=False,
    default=None,
    pattern=r"^[A-Z0-9]{6,10}$"
))

validator.add_parameter(ParameterDefinition(
    name="gift_wrap",
    param_type=ParameterType.BOOLEAN,
    description="Add gift wrapping",
    required=False,
    default=False
))
```

## Testing Your Validators

```python
import pytest
from parameter_validator import ValidationError

def test_valid_translation_request():
    """Test a valid translation"""
    validator = create_translation_validator()
    
    input_data = {
        "type": "prescription",
        "text": "Take two tablets daily",
        "language_origin": "en",
        "translated_language": "es"
    }
    
    result = validator.validate(input_data)
    assert result["type"] == "prescription"
    assert result["confidence_threshold"] == 0.8  # default applied

def test_invalid_language_code():
    """Test invalid language code format"""
    validator = create_translation_validator()
    
    input_data = {
        "type": "symptom",
        "text": "Headache",
        "language_origin": "eng"  # should be 2 chars
    }
    
    with pytest.raises(ValidationError) as exc:
        validator.validate(input_data)
    
    assert "pattern" in str(exc.value).lower()

def test_missing_required_parameter():
    """Test missing required field"""
    validator = create_translation_validator()
    
    with pytest.raises(ValidationError) as exc:
        validator.validate({})  # missing everything
    
    assert "missing" in str(exc.value).lower()
```

## Documentation Generation

Generate beautiful docs for your API:

```python
# Create validator with your parameters
validator = create_translation_validator()

# Generate markdown
docs = validator.generate_documentation()

# Save to file
with open("API_PARAMETERS.md", "w") as f:
    f.write(docs)

# Or serve via web endpoint
@app.route('/docs/parameters')
def api_docs():
    return docs, 200, {'Content-Type': 'text/plain'}
```

## Pro Tips

### Tip 1: Reusable Validators
```python
# Create validators once, use everywhere
USER_VALIDATOR = create_user_validator()
ORDER_VALIDATOR = create_order_validator()

@app.route('/users', methods=['POST'])
@validate_params(USER_VALIDATOR)
def create_user(params):
    # Already validated!
    pass
```

### Tip 2: Combine Multiple Validators
```python
# Base validator for common params
base_validator = ParameterValidator()
base_validator.add_parameter(ParameterDefinition(
    name="api_key",
    param_type=ParameterType.STRING,
    description="API key",
    required=True
))

# Extend for specific endpoints
search_validator = ParameterValidator()
# Copy common params...
search_validator.add_parameter(...specific params...)
```

### Tip 3: Custom Error Responses
```python
try:
    params = validator.validate(request.get_json())
except ValidationError as e:
    return jsonify({
        "success": False,
        "error": "VALIDATION_ERROR",
        "message": str(e),
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": request_id
    }), 400
```

### Tip 4: Log Validation Failures
```python
import logging

logger = logging.getLogger(__name__)

try:
    params = validator.validate(data)
except ValidationError as e:
    logger.warning(f"Validation failed for {endpoint}: {e}")
    logger.debug(f"Invalid data: {data}")
    raise
```

## Next Steps

1. **Customize**: Adapt the examples to your specific needs
2. **Test**: Write comprehensive tests for your validators
3. **Document**: Generate and publish your parameter docs
4. **Monitor**: Track validation errors to improve UX
5. **Iterate**: Add new validators as your API grows

## Need Help?

- Check the main [README.md](README.md) for detailed documentation
- Review [test_parameter_validator.py](test_parameter_validator.py) for more examples
- Explore [flask_api_example.py](flask_api_example.py) for API integration

Happy validating! 🚀
