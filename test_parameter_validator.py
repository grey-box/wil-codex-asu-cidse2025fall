"""
Test Suite for Parameter Validator
Comprehensive tests covering all validation scenarios
"""

import pytest
from parameter_validator import (
    ParameterValidator,
    ParameterDefinition,
    ParameterType,
    ValidationError
)


class TestParameterDefinition:
    """Test parameter definition creation"""
    
    def test_valid_required_parameter(self):
        """Test creating a valid required parameter"""
        param = ParameterDefinition(
            name="user_id",
            param_type=ParameterType.INTEGER,
            description="User ID",
            required=True
        )
        assert param.name == "user_id"
        assert param.required is True
    
    def test_optional_parameter_needs_default(self):
        """Test that optional parameters must have defaults"""
        with pytest.raises(ValueError):
            ParameterDefinition(
                name="optional_param",
                param_type=ParameterType.STRING,
                description="Optional parameter without default",
                required=False
            )
    
    def test_valid_optional_parameter(self):
        """Test creating a valid optional parameter"""
        param = ParameterDefinition(
            name="page_size",
            param_type=ParameterType.INTEGER,
            description="Results per page",
            required=False,
            default=20
        )
        assert param.default == 20


class TestTypeValidation:
    """Test type validation and coercion"""
    
    def setup_method(self):
        """Setup validator before each test"""
        self.validator = ParameterValidator()
    
    def test_string_type_validation(self):
        """Test string type validation"""
        self.validator.add_parameter(ParameterDefinition(
            name="name",
            param_type=ParameterType.STRING,
            description="User name",
            required=True
        ))
        
        result = self.validator.validate({"name": "John Doe"})
        assert result["name"] == "John Doe"
    
    def test_string_coercion(self):
        """Test that numbers are coerced to strings"""
        self.validator.add_parameter(ParameterDefinition(
            name="code",
            param_type=ParameterType.STRING,
            description="Code",
            required=True
        ))
        
        result = self.validator.validate({"code": 12345})
        assert result["code"] == "12345"
        assert isinstance(result["code"], str)
    
    def test_integer_validation(self):
        """Test integer type validation"""
        self.validator.add_parameter(ParameterDefinition(
            name="age",
            param_type=ParameterType.INTEGER,
            description="Age",
            required=True
        ))
        
        result = self.validator.validate({"age": 25})
        assert result["age"] == 25
    
    def test_integer_coercion_from_string(self):
        """Test integer coercion from string"""
        self.validator.add_parameter(ParameterDefinition(
            name="count",
            param_type=ParameterType.INTEGER,
            description="Count",
            required=True
        ))
        
        result = self.validator.validate({"count": "42"})
        assert result["count"] == 42
        assert isinstance(result["count"], int)
    
    def test_invalid_integer(self):
        """Test invalid integer input"""
        self.validator.add_parameter(ParameterDefinition(
            name="amount",
            param_type=ParameterType.INTEGER,
            description="Amount",
            required=True
        ))
        
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate({"amount": "not_a_number"})
        assert "must be an integer" in str(exc_info.value)
    
    def test_float_validation(self):
        """Test float type validation"""
        self.validator.add_parameter(ParameterDefinition(
            name="price",
            param_type=ParameterType.FLOAT,
            description="Price",
            required=True
        ))
        
        result = self.validator.validate({"price": 19.99})
        assert result["price"] == 19.99
    
    def test_boolean_validation(self):
        """Test boolean type validation"""
        self.validator.add_parameter(ParameterDefinition(
            name="active",
            param_type=ParameterType.BOOLEAN,
            description="Is active",
            required=True
        ))
        
        # Test actual boolean
        result = self.validator.validate({"active": True})
        assert result["active"] is True
        
        # Test string coercion
        result = self.validator.validate({"active": "true"})
        assert result["active"] is True
        
        result = self.validator.validate({"active": "false"})
        assert result["active"] is False
    
    def test_list_validation(self):
        """Test list type validation"""
        self.validator.add_parameter(ParameterDefinition(
            name="tags",
            param_type=ParameterType.LIST,
            description="List of tags",
            required=True
        ))
        
        result = self.validator.validate({"tags": ["python", "testing", "validation"]})
        assert isinstance(result["tags"], list)
        assert len(result["tags"]) == 3
    
    def test_dict_validation(self):
        """Test dict type validation"""
        self.validator.add_parameter(ParameterDefinition(
            name="metadata",
            param_type=ParameterType.DICT,
            description="Metadata",
            required=True
        ))
        
        result = self.validator.validate({"metadata": {"key": "value"}})
        assert isinstance(result["metadata"], dict)


class TestConstraints:
    """Test constraint validation"""
    
    def setup_method(self):
        """Setup validator before each test"""
        self.validator = ParameterValidator()
    
    def test_allowed_values(self):
        """Test allowed values constraint"""
        self.validator.add_parameter(ParameterDefinition(
            name="status",
            param_type=ParameterType.STRING,
            description="Status",
            required=True,
            allowed_values=["active", "inactive", "pending"]
        ))
        
        # Valid value
        result = self.validator.validate({"status": "active"})
        assert result["status"] == "active"
        
        # Invalid value
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate({"status": "deleted"})
        assert "must be one of" in str(exc_info.value)
    
    def test_numeric_range(self):
        """Test numeric range constraints"""
        self.validator.add_parameter(ParameterDefinition(
            name="rating",
            param_type=ParameterType.INTEGER,
            description="Rating",
            required=True,
            min_value=1,
            max_value=5
        ))
        
        # Valid value
        result = self.validator.validate({"rating": 3})
        assert result["rating"] == 3
        
        # Too low
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate({"rating": 0})
        assert "must be >=" in str(exc_info.value)
        
        # Too high
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate({"rating": 6})
        assert "must be <=" in str(exc_info.value)
    
    def test_string_length(self):
        """Test string length constraints"""
        self.validator.add_parameter(ParameterDefinition(
            name="username",
            param_type=ParameterType.STRING,
            description="Username",
            required=True,
            min_length=3,
            max_length=20
        ))
        
        # Valid length
        result = self.validator.validate({"username": "john_doe"})
        assert result["username"] == "john_doe"
        
        # Too short
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate({"username": "ab"})
        assert "length >=" in str(exc_info.value)
        
        # Too long
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate({"username": "a" * 25})
        assert "length <=" in str(exc_info.value)
    
    def test_pattern_matching(self):
        """Test regex pattern constraint"""
        self.validator.add_parameter(ParameterDefinition(
            name="email",
            param_type=ParameterType.STRING,
            description="Email address",
            required=True,
            pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        ))
        
        # Valid email
        result = self.validator.validate({"email": "user@example.com"})
        assert result["email"] == "user@example.com"
        
        # Invalid email
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate({"email": "invalid-email"})
        assert "does not match required pattern" in str(exc_info.value)
    
    def test_custom_validator(self):
        """Test custom validation function"""
        def is_even(value):
            return value % 2 == 0
        
        self.validator.add_parameter(ParameterDefinition(
            name="even_number",
            param_type=ParameterType.INTEGER,
            description="Must be even",
            required=True,
            custom_validator=is_even,
            error_message="Number must be even"
        ))
        
        # Valid even number
        result = self.validator.validate({"even_number": 42})
        assert result["even_number"] == 42
        
        # Invalid odd number
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate({"even_number": 43})
        assert "must be even" in str(exc_info.value)


class TestDefaultValues:
    """Test default value handling"""
    
    def setup_method(self):
        """Setup validator before each test"""
        self.validator = ParameterValidator()
    
    def test_default_value_applied(self):
        """Test that default values are applied"""
        self.validator.add_parameter(ParameterDefinition(
            name="page",
            param_type=ParameterType.INTEGER,
            description="Page number",
            required=False,
            default=1
        ))
        
        # No parameter provided
        result = self.validator.validate({})
        assert result["page"] == 1
    
    def test_explicit_value_overrides_default(self):
        """Test that explicit values override defaults"""
        self.validator.add_parameter(ParameterDefinition(
            name="limit",
            param_type=ParameterType.INTEGER,
            description="Results limit",
            required=False,
            default=10
        ))
        
        # Explicit value provided
        result = self.validator.validate({"limit": 25})
        assert result["limit"] == 25


class TestRequiredParameters:
    """Test required parameter validation"""
    
    def setup_method(self):
        """Setup validator before each test"""
        self.validator = ParameterValidator()
    
    def test_missing_required_parameter(self):
        """Test that missing required parameters raise errors"""
        self.validator.add_parameter(ParameterDefinition(
            name="api_key",
            param_type=ParameterType.STRING,
            description="API key",
            required=True
        ))
        
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate({})
        assert "Required parameter 'api_key' is missing" in str(exc_info.value)
    
    def test_custom_error_message(self):
        """Test custom error messages"""
        self.validator.add_parameter(ParameterDefinition(
            name="token",
            param_type=ParameterType.STRING,
            description="Auth token",
            required=True,
            error_message="Authentication token is required for this operation"
        ))
        
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate({})
        assert "Authentication token is required" in str(exc_info.value)


class TestUnexpectedParameters:
    """Test handling of unexpected parameters"""
    
    def setup_method(self):
        """Setup validator before each test"""
        self.validator = ParameterValidator()
    
    def test_unexpected_parameters_rejected(self):
        """Test that unexpected parameters are rejected"""
        self.validator.add_parameter(ParameterDefinition(
            name="id",
            param_type=ParameterType.INTEGER,
            description="ID",
            required=True
        ))
        
        with pytest.raises(ValidationError) as exc_info:
            self.validator.validate({"id": 1, "extra_param": "value"})
        assert "Unexpected parameters" in str(exc_info.value)


class TestDocumentationGeneration:
    """Test documentation generation"""
    
    def test_generate_markdown_docs(self):
        """Test markdown documentation generation"""
        validator = ParameterValidator()
        
        validator.add_parameter(ParameterDefinition(
            name="user_id",
            param_type=ParameterType.INTEGER,
            description="User identifier",
            required=True
        ))
        
        validator.add_parameter(ParameterDefinition(
            name="format",
            param_type=ParameterType.STRING,
            description="Output format",
            required=False,
            default="json",
            allowed_values=["json", "xml", "csv"]
        ))
        
        docs = validator.generate_documentation()
        
        # Check that docs contain expected content
        assert "# Parameter Definitions" in docs
        assert "user_id" in docs
        assert "format" in docs
        assert "**Required:**" in docs
        assert "**Default:**" in docs
        assert "**Allowed Values:**" in docs


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
