"""
Field Models Module

This module defines the field types and their associated validation logic
for the Teable API client.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from ..exceptions import ValidationError


class FieldType(str, Enum):
    """Enumeration of supported field types in Teable."""
    SINGLE_LINE_TEXT = "singleLineText"
    LONG_TEXT = "longText"
    USER = "user"
    ATTACHMENT = "attachment"
    CHECKBOX = "checkbox"
    MULTIPLE_SELECT = "multipleSelect"
    SINGLE_SELECT = "singleSelect"
    DATE = "date"
    NUMBER = "number"
    DURATION = "duration"
    RATING = "rating"
    FORMULA = "formula"
    ROLLUP = "rollup"
    COUNT = "count"
    LINK = "link"
    CREATED_TIME = "createdTime"
    LAST_MODIFIED_TIME = "lastModifiedTime"
    CREATED_BY = "createdBy"
    LAST_MODIFIED_BY = "lastModifiedBy"
    AUTO_NUMBER = "autoNumber"
    BUTTON = "button"


@dataclass
class FieldOption:
    """
    Base class for field-specific options.
    
    This class serves as a base for more specific option types
    that different fields might require.
    """
    pass


@dataclass
class SelectOption(FieldOption):
    """Options for single and multiple select fields."""
    choices: List[str]
    default_value: Optional[Union[str, List[str]]] = None

    def validate_value(self, value: Union[str, List[str]]) -> None:
        """
        Validate a value against the available choices.
        
        Args:
            value: String for single select, list of strings for multiple select
            
        Raises:
            ValidationError: If value is invalid
        """
        if isinstance(value, str):
            if value not in self.choices:
                raise ValidationError(f"Value '{value}' not in choices: {self.choices}")
        elif isinstance(value, list):
            invalid_values = [v for v in value if v not in self.choices]
            if invalid_values:
                raise ValidationError(
                    f"Values {invalid_values} not in choices: {self.choices}"
                )


@dataclass
class NumberOption(FieldOption):
    """Options for number fields."""
    precision: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    format: Optional[str] = None

    def validate_value(self, value: Union[int, float]) -> None:
        """
        Validate a numeric value against constraints.
        
        Args:
            value: Number to validate
            
        Raises:
            ValidationError: If value is invalid
        """
        if not isinstance(value, (int, float)):
            raise ValidationError(f"Expected number, got {type(value)}")
        
        if self.min_value is not None and value < self.min_value:
            raise ValidationError(f"Value {value} below minimum {self.min_value}")
        
        if self.max_value is not None and value > self.max_value:
            raise ValidationError(f"Value {value} above maximum {self.max_value}")


@dataclass
class DateOption(FieldOption):
    """Options for date fields."""
    format: Optional[str] = None
    include_time: bool = True
    timezone: Optional[str] = None

    def validate_value(self, value: Union[str, datetime]) -> None:
        """
        Validate a date value.
        
        Args:
            value: Date string or datetime object
            
        Raises:
            ValidationError: If value is invalid
        """
        if isinstance(value, str):
            try:
                datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError as e:
                raise ValidationError(f"Invalid date format: {str(e)}")
        elif not isinstance(value, datetime):
            raise ValidationError(
                f"Expected string or datetime, got {type(value)}"
            )


@dataclass
class Field:
    """
    Represents a field/column in a Teable table.
    
    Attributes:
        field_id (str): Unique identifier for the field
        name (str): Display name of the field
        field_type (FieldType): Type of the field
        description (Optional[str]): Field description
        options (Optional[FieldOption]): Field-specific options
        is_primary (bool): Whether this is the primary field
        is_required (bool): Whether the field is required
        is_computed (bool): Whether the field is computed (formula/rollup)
    """
    field_id: str
    name: str
    field_type: FieldType
    description: Optional[str] = None
    options: Optional[FieldOption] = None
    is_primary: bool = False
    is_required: bool = False
    is_computed: bool = False

    def validate_value(self, value: Any) -> None:
        """
        Validate a value for this field.
        
        Args:
            value: Value to validate
            
        Raises:
            ValidationError: If value is invalid for this field type
        """
        if value is None:
            if self.is_required:
                raise ValidationError(f"Field '{self.name}' is required")
            return

        if self.is_computed:
            raise ValidationError(
                f"Field '{self.name}' is computed and cannot be set directly"
            )

        if self.field_type in {FieldType.SINGLE_SELECT, FieldType.MULTIPLE_SELECT}:
            if not isinstance(self.options, SelectOption):
                raise ValidationError("Field options not properly configured")
            self.options.validate_value(value)

        elif self.field_type == FieldType.NUMBER:
            if not isinstance(self.options, NumberOption):
                raise ValidationError("Field options not properly configured")
            self.options.validate_value(value)

        elif self.field_type == FieldType.DATE:
            if not isinstance(self.options, DateOption):
                raise ValidationError("Field options not properly configured")
            self.options.validate_value(value)

        elif self.field_type == FieldType.CHECKBOX:
            if not isinstance(value, bool):
                raise ValidationError(f"Expected boolean, got {type(value)}")

        elif self.field_type in {FieldType.SINGLE_LINE_TEXT, FieldType.LONG_TEXT}:
            if not isinstance(value, str):
                raise ValidationError(f"Expected string, got {type(value)}")

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'Field':
        """
        Create a Field instance from API response data.
        
        Args:
            data: Dictionary containing field data from API
            
        Returns:
            Field: New field instance
        """
        field_type = FieldType(data['type'])
        options = None

        if field_type in {FieldType.SINGLE_SELECT, FieldType.MULTIPLE_SELECT}:
            options = SelectOption(
                choices=data.get('options', {}).get('choices', []),
                default_value=data.get('options', {}).get('defaultValue')
            )
        elif field_type == FieldType.NUMBER:
            options = NumberOption(
                precision=data.get('options', {}).get('precision'),
                min_value=data.get('options', {}).get('minValue'),
                max_value=data.get('options', {}).get('maxValue'),
                format=data.get('options', {}).get('format')
            )
        elif field_type == FieldType.DATE:
            options = DateOption(
                format=data.get('options', {}).get('format'),
                include_time=data.get('options', {}).get('includeTime', True),
                timezone=data.get('options', {}).get('timezone')
            )

        return cls(
            field_id=data['id'],
            name=data['name'],
            field_type=field_type,
            description=data.get('description'),
            options=options,
            is_primary=data.get('isPrimary', False),
            is_required=data.get('isRequired', False),
            is_computed=data.get('isComputed', False)
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert field to dictionary format for API requests.
        
        Returns:
            dict: Field data as dictionary
        """
        result = {
            'id': self.field_id,
            'name': self.name,
            'type': self.field_type.value,
            'isPrimary': self.is_primary,
            'isRequired': self.is_required,
            'isComputed': self.is_computed
        }

        if self.description:
            result['description'] = self.description

        if self.options:
            result['options'] = {}
            if isinstance(self.options, SelectOption):
                result['options']['choices'] = self.options.choices
                if self.options.default_value:
                    result['options']['defaultValue'] = self.options.default_value
            elif isinstance(self.options, NumberOption):
                if self.options.precision is not None:
                    result['options']['precision'] = self.options.precision
                if self.options.min_value is not None:
                    result['options']['minValue'] = self.options.min_value
                if self.options.max_value is not None:
                    result['options']['maxValue'] = self.options.max_value
                if self.options.format:
                    result['options']['format'] = self.options.format
            elif isinstance(self.options, DateOption):
                if self.options.format:
                    result['options']['format'] = self.options.format
                result['options']['includeTime'] = self.options.include_time
                if self.options.timezone:
                    result['options']['timezone'] = self.options.timezone

        return result
