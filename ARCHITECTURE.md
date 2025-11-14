# System Architecture

## Component Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Your Application                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Parameter Validator                          │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  1. Receive Input Parameters (dict)                    │    │
│  └────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  2. Check Required Parameters                          │    │
│  │     • Are all required params present?                 │    │
│  │     • Apply defaults for missing optional params       │    │
│  └────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  3. Type Validation & Coercion                         │    │
│  │     • Validate data types                              │    │
│  │     • Coerce compatible types (e.g., "42" → 42)        │    │
│  └────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  4. Constraint Validation                              │    │
│  │     • Allowed values (enums)                           │    │
│  │     • Numeric ranges (min/max)                         │    │
│  │     • String length                                    │    │
│  │     • Pattern matching (regex)                         │    │
│  │     • Custom validators                                │    │
│  └────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  5. Check for Unexpected Parameters                    │    │
│  └────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                     ┌────────┴────────┐                         │
│                     │                 │                         │
│                  Valid            Invalid                       │
│                     │                 │                         │
│                     ▼                 ▼                         │
│         ┌──────────────────┐  ┌──────────────────┐            │
│         │ Return Validated │  │ Raise Validation │            │
│         │   Parameters     │  │     Error        │            │
│         └──────────────────┘  └──────────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

## Class Structure

```
ParameterType (Enum)
├── STRING
├── INTEGER
├── FLOAT
├── BOOLEAN
├── LIST
└── DICT

ParameterDefinition (dataclass)
├── name: str
├── param_type: ParameterType
├── description: str
├── required: bool
├── default: Any
├── allowed_values: List[Any]
├── min_value: Union[int, float]
├── max_value: Union[int, float]
├── min_length: int
├── max_length: int
├── pattern: str (regex)
├── custom_validator: Callable
└── error_message: str

ParameterValidator
├── parameters: Dict[str, ParameterDefinition]
├── add_parameter(param_def)
├── validate(input_params) → Dict[str, Any]
├── _validate_parameter(...)
├── _validate_type(...)
└── generate_documentation() → str
```

## Data Flow Example

### Translation API Request

```
Step 1: HTTP Request
POST /translate
{
  "type": "prescription",
  "text": "Take two tablets daily",
  "language_origin": "en"
}

Step 2: Parameter Validator Receives
{
  "type": "prescription",           ← Present
  "text": "Take two tablets daily", ← Present
  "language_origin": "en",          ← Present
  "translated_language": ???,       ← Missing (optional)
  "confidence_threshold": ???       ← Missing (optional)
}

Step 3: Apply Defaults
{
  "type": "prescription",
  "text": "Take two tablets daily",
  "language_origin": "en",
  "translated_language": "en",      ← Default applied
  "confidence_threshold": 0.8       ← Default applied
}

Step 4: Type Validation
✓ type: string
✓ text: string
✓ language_origin: string
✓ translated_language: string
✓ confidence_threshold: float

Step 5: Constraint Validation
✓ type in ["prescription", "symptom"]
✓ text length: 1 ≤ 23 ≤ 5000
✓ language_origin matches ^[a-z]{2}$
✓ translated_language matches ^[a-z]{2}$
✓ confidence_threshold: 0.0 ≤ 0.8 ≤ 1.0

Step 6: Return Validated Parameters
{
  "type": "prescription",
  "text": "Take two tablets daily",
  "language_origin": "en",
  "translated_language": "en",
  "confidence_threshold": 0.8
}
```

## Integration Patterns

### Pattern 1: Direct Usage

```python
validator = ParameterValidator()
# ... define parameters ...

try:
    params = validator.validate(request_data)
    result = process(params)
except ValidationError as e:
    return error_response(str(e))
```

### Pattern 2: Decorator Pattern (Flask)

```python
@validate_params(validator)
def endpoint(params):
    # params already validated
    return process(params)
```

### Pattern 3: Middleware Pattern

```python
class ValidationMiddleware:
    def __init__(self, app, validators):
        self.app = app
        self.validators = validators
    
    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        if path in self.validators:
            # validate before passing to app
            pass
        return self.app(environ, start_response)
```

## Error Handling Flow

```
Input Parameters
      │
      ▼
┌──────────────┐
│  Validate    │
└──────────────┘
      │
      ├─── Validation Success ──→ Continue Processing
      │
      └─── Validation Error
                │
                ▼
          ┌─────────────────────┐
          │  Collect All Errors │
          └─────────────────────┘
                │
                ▼
          ┌─────────────────────┐
          │   Format Error      │
          │   Message           │
          └─────────────────────┘
                │
                ▼
          ┌─────────────────────┐
          │  Return 400         │
          │  Bad Request        │
          └─────────────────────┘
```

## Validation Rules Priority

```
1. Required Check
   ↓
2. Type Validation
   ↓
3. Allowed Values (if defined)
   ↓
4. Min/Max Values (if defined)
   ↓
5. Length Constraints (if defined)
   ↓
6. Pattern Matching (if defined)
   ↓
7. Custom Validator (if defined)
```

## Performance Considerations

```
Validation Step             Avg Time    Notes
─────────────────────────────────────────────────
Required check              < 1μs       Dict lookup
Type validation             1-5μs       Depends on coercion
Allowed values check        1-2μs       List/set lookup
Numeric range check         < 1μs       Simple comparison
String length check         < 1μs       len() call
Pattern matching            5-50μs      Regex compilation cached
Custom validator            Varies      User-defined

Total per parameter:        ~10-100μs
Total for 10 parameters:    ~100-1000μs (0.1-1ms)
```

## Memory Usage

```
Component                   Memory      Notes
────────────────────────────────────────────────
ParameterDefinition         ~500 bytes  Per parameter
ParameterValidator          ~5KB        Base + parameters
Validated result            ~1KB        Depends on data
Error messages              ~500 bytes  When validation fails
```

## Extensibility Points

```
1. Custom Parameter Types
   └── Add new ParameterType enum values
   └── Implement validation in _validate_type()

2. Custom Validators
   └── Pass callable to custom_validator
   └── Return bool or raise exception

3. Custom Error Formatting
   └── Override ValidationError formatting
   └── Implement custom error handler

4. Documentation Templates
   └── Modify generate_documentation()
   └── Add custom output formats

5. Integration Adapters
   └── Create decorators for frameworks
   └── Build middleware classes
```

## Security Considerations

```
✓ Input Sanitization
  └── All inputs validated before use
  └── Type coercion prevents injection

✓ DoS Prevention
  └── Max length limits on strings
  └── Max value limits on numbers
  └── Fast validation (no complex operations)

✓ Error Message Safety
  └── No sensitive data in error messages
  └── Configurable error verbosity

⚠ Note: This validates structure, not content security
  └── Use additional security measures for:
      • SQL injection prevention
      • XSS protection
      • CSRF tokens
      • Authentication/Authorization
```

## Testing Strategy

```
Unit Tests
├── Test each parameter type
├── Test each constraint type
├── Test edge cases (empty, null, max values)
├── Test error messages
└── Test default value application

Integration Tests
├── Test with Flask endpoints
├── Test decorator functionality
├── Test error handling
└── Test documentation generation

Performance Tests
├── Benchmark validation speed
├── Test with large parameter sets
└── Profile memory usage
```

## Deployment Checklist

```
□ Define all parameters with clear descriptions
□ Set appropriate min/max values for security
□ Write custom validators for business rules
□ Generate and publish API documentation
□ Add comprehensive error handling
□ Write unit tests (>80% coverage)
□ Add integration tests
□ Set up monitoring for validation errors
□ Document all endpoints
□ Review security implications
```

