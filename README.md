# Parameter & Constraint Specialist System

A robust, production-ready parameter validation system for Python applications. Define input parameters, defaults, and constraints with comprehensive validation rules.

## 🎯 Features

- **Type Validation**: String, Integer, Float, Boolean, List, Dict
- **Constraint Checking**: Allowed values, ranges, length limits, regex patterns
- **Custom Validators**: Add your own validation logic
- **Default Values**: Automatic application of defaults for optional parameters
- **Error Handling**: Clear, actionable error messages
- **Documentation Generation**: Auto-generate markdown docs from parameter definitions
- **API Integration**: Easy integration with Flask and other web frameworks
- **Type Coercion**: Smart conversion between compatible types

## 📦 Installation

```bash
# Clone or download the files
pip install -r requirements.txt
```

## 🚀 Quick Start

### Basic Usage

```python
from parameter_validator import (
    ParameterValidator,
    ParameterDefinition,
    ParameterType,
    ValidationError
)

# Create validator
validator = ParameterValidator()

# Define a parameter
validator.add_parameter(ParameterDefinition(
    name="language",
    param_type=ParameterType.STRING,
    description="Language code",
    required=True,
    allowed_values=["en", "es", "fr"],
    pattern=r"^[a-z]{2}$"
))

# Validate input
try:
    result = validator.validate({"language": "en"})
    print(f"Valid! Language: {result['language']}")
except ValidationError as e:
    print(f"Invalid: {e}")
```

### Running the Demo

```bash
# Run the standalone demo
python parameter_validator.py
```

Output shows multiple test cases with validation results.

## 🌐 API Server Example

### Start the Flask API

```bash
python flask_api_example.py
```

The server starts on `http://localhost:5000` with these endpoints:

- `GET /` - API information
- `POST /translate` - Translate text (with validation)
- `GET /search` - Search content (with validation)
- `GET /docs/translate` - Parameter documentation
- `GET /docs/search` - Parameter documentation

### Using the API

**Translation Request:**
```bash
curl -X POST http://localhost:5000/translate \
  -H "Content-Type: application/json" \
  -d '{
    "type": "prescription",
    "text": "Take two tablets daily",
    "language_origin": "en",
    "translated_language": "es"
  }'
```

**Search Request:**
```bash
curl "http://localhost:5000/search?query=medical&limit=5&sort_by=date"
```

### Using the Python Client

```python
from api_client_example import TranslationAPIClient

client = TranslationAPIClient()

# Translate
result = client.translate(
    text="Take medicine with food",
    content_type="prescription",
    language_origin="en",
    translated_language="es"
)

# Search
results = client.search(
    query="symptoms",
    limit=10,
    sort_by="relevance"
)
```

Or run the full client demo:
```bash
python api_client_example.py
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest test_parameter_validator.py -v

# Run with coverage
pytest test_parameter_validator.py --cov=parameter_validator --cov-report=html

# Run specific test class
pytest test_parameter_validator.py::TestTypeValidation -v
```

## 📚 Parameter Definition Options

### Required vs Optional

```python
# Required parameter (must provide value)
ParameterDefinition(
    name="user_id",
    param_type=ParameterType.INTEGER,
    description="User identifier",
    required=True
)

# Optional parameter (uses default if not provided)
ParameterDefinition(
    name="page_size",
    param_type=ParameterType.INTEGER,
    description="Results per page",
    required=False,
    default=20
)
```

### Type Options

```python
ParameterType.STRING   # Text values
ParameterType.INTEGER  # Whole numbers
ParameterType.FLOAT    # Decimal numbers
ParameterType.BOOLEAN  # True/False
ParameterType.LIST     # Arrays
ParameterType.DICT     # Objects/Maps
```

### Constraint Options

```python
ParameterDefinition(
    name="rating",
    param_type=ParameterType.INTEGER,
    description="Product rating",
    required=True,
    
    # Allowed values (enum-like)
    allowed_values=[1, 2, 3, 4, 5],
    
    # Numeric ranges
    min_value=1,
    max_value=5,
    
    # String/list length
    min_length=1,
    max_length=100,
    
    # Regex pattern
    pattern=r"^\d+$",
    
    # Custom validation function
    custom_validator=lambda x: x % 2 == 0,
    
    # Custom error message
    error_message="Rating must be between 1 and 5"
)
```

## 🎨 Real-World Examples

### Translation API (from your image)

```python
validator = ParameterValidator()

validator.add_parameter(ParameterDefinition(
    name="type",
    param_type=ParameterType.STRING,
    description="Type of medical content",
    required=True,
    allowed_values=["prescription", "symptom"]
))

validator.add_parameter(ParameterDefinition(
    name="language_origin",
    param_type=ParameterType.STRING,
    description="Source language (ISO 639-1)",
    required=False,
    default="en",
    pattern=r"^[a-z]{2}$"
))

validator.add_parameter(ParameterDefinition(
    name="text",
    param_type=ParameterType.STRING,
    description="Text to translate",
    required=True,
    min_length=1,
    max_length=5000
))
```

### E-commerce API

```python
validator = ParameterValidator()

validator.add_parameter(ParameterDefinition(
    name="product_id",
    param_type=ParameterType.STRING,
    description="Product SKU",
    required=True,
    pattern=r"^[A-Z]{3}-\d{6}$"
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
    name="coupon_code",
    param_type=ParameterType.STRING,
    description="Discount code",
    required=False,
    default=None,
    pattern=r"^[A-Z0-9]{6,10}$"
))
```

### User Registration

```python
def validate_password_strength(password):
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_upper and has_lower and has_digit

validator.add_parameter(ParameterDefinition(
    name="email",
    param_type=ParameterType.STRING,
    description="User email",
    required=True,
    pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
))

validator.add_parameter(ParameterDefinition(
    name="password",
    param_type=ParameterType.STRING,
    description="User password",
    required=True,
    min_length=8,
    max_length=128,
    custom_validator=validate_password_strength,
    error_message="Password must contain uppercase, lowercase, and digits"
))

validator.add_parameter(ParameterDefinition(
    name="age",
    param_type=ParameterType.INTEGER,
    description="User age",
    required=True,
    min_value=13,
    max_value=120
))
```

## 🔧 Integration with Flask

Use the `@validate_params` decorator:

```python
from flask import Flask
from parameter_validator import ParameterValidator, ParameterDefinition, ParameterType

app = Flask(__name__)

# Create validator
user_validator = ParameterValidator()
user_validator.add_parameter(ParameterDefinition(
    name="username",
    param_type=ParameterType.STRING,
    description="Username",
    required=True,
    min_length=3,
    max_length=20
))

@app.route("/user", methods=["POST"])
@validate_params(user_validator)
def create_user(params):
    # params are already validated!
    return {"message": f"User {params['username']} created"}
```

## 📖 Documentation Generation

Generate markdown documentation automatically:

```python
validator = ParameterValidator()
# ... add parameters ...

markdown = validator.generate_documentation()
print(markdown)
```

Output:
```markdown
# Parameter Definitions

Complete list of parameters, types, defaults, and validation rules.

## language_origin

**Description:** Source language code (ISO 639-1)

**Type:** `string`

**Required:** No

**Default:** `en`

**Pattern:** `^[a-z]{2}$`

---
```

## 🎯 Best Practices

1. **Always provide descriptions** - Help users understand each parameter
2. **Use meaningful error messages** - Guide users to fix issues
3. **Set sensible defaults** - Reduce friction for common use cases
4. **Validate early** - Catch errors before processing
5. **Document everything** - Use the auto-generation feature
6. **Test thoroughly** - Cover all validation paths
7. **Be consistent** - Use the same patterns across your API

## 📊 Performance

The validation system is designed for production use:

- Fast validation (microseconds per parameter)
- Minimal memory footprint
- No external dependencies for core functionality
- Thread-safe

## 🤝 Contributing

Ideas for enhancements:
- Add more parameter types (URL, Email, Date, etc.)
- Implement parameter dependencies (if X then Y required)
- Add async validation support
- Create JSON Schema export
- Build OpenAPI/Swagger integration

## 📄 License

This is sample code for educational and commercial use.

## 🔗 Resources

- **Validation Patterns**: Clean Code by Robert Martin
- **API Design**: RESTful API Design by Microsoft
- **Python Type Hints**: PEP 484, 585, 604

## 💡 Next Steps

1. Customize the parameter definitions for your use case
2. Add custom validators for domain-specific logic
3. Integrate with your existing API framework
4. Generate and publish parameter documentation
5. Add monitoring/logging for validation failures

---

Built for robust parameter validation in production systems. 🚀
