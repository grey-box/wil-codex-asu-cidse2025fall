"""
Parameter & Constraint Specialist
A robust system for defining, validating, and managing input parameters
"""

from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import re


class ParameterType(Enum):
    """Supported parameter types"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"


class ValidationError(Exception):
    """Custom exception for parameter validation errors"""
    pass


@dataclass
class ParameterDefinition:
    """
    Defines a single parameter with all its constraints and validation rules
    """
    name: str
    param_type: ParameterType
    description: str
    required: bool = True
    default: Any = None
    allowed_values: Optional[List[Any]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    custom_validator: Optional[Callable] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """Validate the definition itself"""
        if not self.required and self.default is None:
            raise ValueError(f"Optional parameter '{self.name}' must have a default value")


class ParameterValidator:
    """
    Main validator class that manages all parameter definitions and validation
    """
    
    def __init__(self):
        self.parameters: Dict[str, ParameterDefinition] = {}
    
    def add_parameter(self, param_def: ParameterDefinition) -> None:
        """Register a new parameter definition"""
        self.parameters[param_def.name] = param_def
    
    def validate(self, input_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate input parameters against defined constraints
        Returns validated and normalized parameters with defaults applied
        """
        validated = {}
        errors = []
        
        # Check all defined parameters
        for name, param_def in self.parameters.items():
            try:
                value = self._validate_parameter(name, input_params.get(name), param_def)
                validated[name] = value
            except ValidationError as e:
                errors.append(str(e))
        
        # Check for unexpected parameters
        unexpected = set(input_params.keys()) - set(self.parameters.keys())
        if unexpected:
            errors.append(f"Unexpected parameters: {', '.join(unexpected)}")
        
        if errors:
            raise ValidationError("\n".join(errors))
        
        return validated
    
    def _validate_parameter(self, name: str, value: Any, param_def: ParameterDefinition) -> Any:
        """Validate a single parameter"""
        
        # Handle missing parameters
        if value is None:
            if param_def.required:
                raise ValidationError(
                    param_def.error_message or 
                    f"Required parameter '{name}' is missing"
                )
            return param_def.default
        
        # Type validation
        value = self._validate_type(name, value, param_def)
        
        # Allowed values check
        if param_def.allowed_values is not None:
            if value not in param_def.allowed_values:
                raise ValidationError(
                    f"Parameter '{name}' must be one of {param_def.allowed_values}, got '{value}'"
                )
        
        # Numeric range checks
        if param_def.min_value is not None and value < param_def.min_value:
            raise ValidationError(
                f"Parameter '{name}' must be >= {param_def.min_value}, got {value}"
            )
        
        if param_def.max_value is not None and value > param_def.max_value:
            raise ValidationError(
                f"Parameter '{name}' must be <= {param_def.max_value}, got {value}"
            )
        
        # String length checks
        if param_def.min_length is not None and len(str(value)) < param_def.min_length:
            raise ValidationError(
                f"Parameter '{name}' must have length >= {param_def.min_length}"
            )
        
        if param_def.max_length is not None and len(str(value)) > param_def.max_length:
            raise ValidationError(
                f"Parameter '{name}' must have length <= {param_def.max_length}"
            )
        
        # Pattern matching for strings
        if param_def.pattern and isinstance(value, str):
            if not re.match(param_def.pattern, value):
                raise ValidationError(
                    f"Parameter '{name}' does not match required pattern: {param_def.pattern}"
                )
        
        # Custom validation
        if param_def.custom_validator:
            if not param_def.custom_validator(value):
                raise ValidationError(
                    param_def.error_message or 
                    f"Parameter '{name}' failed custom validation"
                )
        
        return value
    
    def _validate_type(self, name: str, value: Any, param_def: ParameterDefinition) -> Any:
        """Validate and coerce parameter type"""
        
        if param_def.param_type == ParameterType.STRING:
            if not isinstance(value, str):
                return str(value)  # Coerce to string
            return value
        
        elif param_def.param_type == ParameterType.INTEGER:
            try:
                return int(value)
            except (ValueError, TypeError):
                raise ValidationError(
                    f"Parameter '{name}' must be an integer, got '{value}'"
                )
        
        elif param_def.param_type == ParameterType.FLOAT:
            try:
                return float(value)
            except (ValueError, TypeError):
                raise ValidationError(
                    f"Parameter '{name}' must be a float, got '{value}'"
                )
        
        elif param_def.param_type == ParameterType.BOOLEAN:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                if value.lower() in ('true', '1', 'yes'):
                    return True
                if value.lower() in ('false', '0', 'no'):
                    return False
            raise ValidationError(
                f"Parameter '{name}' must be a boolean, got '{value}'"
            )
        
        elif param_def.param_type == ParameterType.LIST:
            if not isinstance(value, list):
                raise ValidationError(
                    f"Parameter '{name}' must be a list, got {type(value).__name__}"
                )
            return value
        
        elif param_def.param_type == ParameterType.DICT:
            if not isinstance(value, dict):
                raise ValidationError(
                    f"Parameter '{name}' must be a dict, got {type(value).__name__}"
                )
            return value
        
        return value
    
    def generate_documentation(self) -> str:
        """Generate markdown documentation for all parameters"""
        doc = "# Parameter Definitions\n\n"
        doc += "Complete list of parameters, types, defaults, and validation rules.\n\n"
        
        for name, param in self.parameters.items():
            doc += f"## {name}\n\n"
            doc += f"**Description:** {param.description}\n\n"
            doc += f"**Type:** `{param.param_type.value}`\n\n"
            doc += f"**Required:** {'Yes' if param.required else 'No'}\n\n"
            
            if param.default is not None:
                doc += f"**Default:** `{param.default}`\n\n"
            
            if param.allowed_values:
                doc += f"**Allowed Values:** {', '.join(f'`{v}`' for v in param.allowed_values)}\n\n"
            
            if param.min_value is not None or param.max_value is not None:
                range_str = f"{param.min_value or '-∞'} to {param.max_value or '∞'}"
                doc += f"**Range:** {range_str}\n\n"
            
            if param.min_length is not None or param.max_length is not None:
                length_str = f"{param.min_length or 0} to {param.max_length or 'unlimited'} characters"
                doc += f"**Length:** {length_str}\n\n"
            
            if param.pattern:
                doc += f"**Pattern:** `{param.pattern}`\n\n"
            
            doc += "---\n\n"
        
        return doc


# Example: Translation API Parameters (from your image)
def create_translation_validator() -> ParameterValidator:
    """
    Create a validator for a translation API based on your image
    """
    validator = ParameterValidator()
    
    # Type parameter
    validator.add_parameter(ParameterDefinition(
        name="type",
        param_type=ParameterType.STRING,
        description="Type of content being translated",
        required=True,
        allowed_values=["prescription", "symptom"],
        error_message="Type must be either 'prescription' or 'symptom'"
    ))
    
    # Language origin
    validator.add_parameter(ParameterDefinition(
        name="language_origin",
        param_type=ParameterType.STRING,
        description="Source language code (ISO 639-1)",
        required=False,
        default="en",
        pattern=r"^[a-z]{2}$",
        error_message="Language code must be 2 lowercase letters (e.g., 'en', 'es', 'fr')"
    ))
    
    # Translated language
    validator.add_parameter(ParameterDefinition(
        name="translated_language",
        param_type=ParameterType.STRING,
        description="Target language code (ISO 639-1)",
        required=False,
        default="en",
        pattern=r"^[a-z]{2}$",
        error_message="Language code must be 2 lowercase letters (e.g., 'en', 'es', 'fr')"
    ))
    
    # Text content
    validator.add_parameter(ParameterDefinition(
        name="text",
        param_type=ParameterType.STRING,
        description="Text to be translated",
        required=True,
        min_length=1,
        max_length=5000,
        error_message="Text must be between 1 and 5000 characters"
    ))
    
    # Confidence threshold
    validator.add_parameter(ParameterDefinition(
        name="confidence_threshold",
        param_type=ParameterType.FLOAT,
        description="Minimum confidence score for translation",
        required=False,
        default=0.8,
        min_value=0.0,
        max_value=1.0
    ))
    
    return validator


# Demo usage
if __name__ == "__main__":
    print("=" * 60)
    print("Parameter & Constraint Specialist - Demo")
    print("=" * 60)
    
    # Create validator
    validator = create_translation_validator()
    
    # Generate documentation
    print("\n📄 Generated Documentation:\n")
    print(validator.generate_documentation()[:500] + "...\n")
    
    # Test Case 1: Valid input
    print("\n✅ Test Case 1: Valid Input")
    print("-" * 60)
    try:
        valid_input = {
            "type": "prescription",
            "language_origin": "en",
            "translated_language": "es",
            "text": "Take two tablets daily"
        }
        result = validator.validate(valid_input)
        print(f"Input: {valid_input}")
        print(f"✓ Validation passed!")
        print(f"Result: {result}")
    except ValidationError as e:
        print(f"✗ Validation failed: {e}")
    
    # Test Case 2: Missing required parameter
    print("\n\n❌ Test Case 2: Missing Required Parameter")
    print("-" * 60)
    try:
        invalid_input = {
            "language_origin": "en",
            "translated_language": "es"
        }
        result = validator.validate(invalid_input)
        print(f"✓ Validation passed!")
    except ValidationError as e:
        print(f"Input: {invalid_input}")
        print(f"✗ Validation failed:\n{e}")
    
    # Test Case 3: Invalid type value
    print("\n\n❌ Test Case 3: Invalid Allowed Value")
    print("-" * 60)
    try:
        invalid_input = {
            "type": "diagnosis",  # Not in allowed values
            "text": "Patient has fever"
        }
        result = validator.validate(invalid_input)
        print(f"✓ Validation passed!")
    except ValidationError as e:
        print(f"Input: {invalid_input}")
        print(f"✗ Validation failed:\n{e}")
    
    # Test Case 4: Uses defaults
    print("\n\n✅ Test Case 4: Using Default Values")
    print("-" * 60)
    try:
        input_with_defaults = {
            "type": "symptom",
            "text": "Headache and nausea"
        }
        result = validator.validate(input_with_defaults)
        print(f"Input: {input_with_defaults}")
        print(f"✓ Validation passed!")
        print(f"Result with defaults: {result}")
    except ValidationError as e:
        print(f"✗ Validation failed: {e}")
    
    # Test Case 5: Invalid pattern
    print("\n\n❌ Test Case 5: Invalid Pattern (Language Code)")
    print("-" * 60)
    try:
        invalid_input = {
            "type": "prescription",
            "language_origin": "eng",  # Should be 2 letters
            "text": "Take medication"
        }
        result = validator.validate(invalid_input)
        print(f"✓ Validation passed!")
    except ValidationError as e:
        print(f"Input: {invalid_input}")
        print(f"✗ Validation failed:\n{e}")
    
    print("\n" + "=" * 60)
