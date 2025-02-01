"""
View Models Module

This module defines the view-related models and query building functionality
for the Teable API client.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict, Union

QueryParams = Dict[str, Union[str, int, List[Dict[str, Any]], List[Any]]]

from .field import Field


class Position(str, Enum):
    """Enumeration of position options."""
    BEFORE = "before"
    AFTER = "after"


class SortDirection(str, Enum):
    """Enumeration of sort directions."""
    ASCENDING = "asc"
    DESCENDING = "desc"


class FilterOperator(str, Enum):
    """Enumeration of filter operators."""
    EQUALS = "="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUALS = ">="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUALS = "<="
    CONTAINS = "contains"
    NOT_CONTAINS = "notContains"
    STARTS_WITH = "startsWith"
    ENDS_WITH = "endsWith"
    IS_EMPTY = "isEmpty"
    IS_NOT_EMPTY = "isNotEmpty"
    IN = "in"
    NOT_IN = "notIn"
    BETWEEN = "between"


@dataclass
class FilterCondition:
    """
    Represents a single filter condition.
    
    Attributes:
        field (Union[str, Field]): Field to filter on
        operator (FilterOperator): Comparison operator
        value (Any): Value to compare against
    """
    field: Union[str, Field]
    operator: FilterOperator
    value: Any

    def to_dict(self) -> Dict[str, Any]:
        """Convert filter condition to dictionary format."""
        return {
            'fieldId': self.field.field_id if isinstance(self.field, Field) else self.field,
            'operator': self.operator.value,
            'value': self.value
        }


@dataclass
class SortCondition:
    """
    Represents a sort condition.
    
    Attributes:
        field (Union[str, Field]): Field to sort by
        direction (SortDirection): Sort direction
    """
    field: Union[str, Field]
    direction: SortDirection = SortDirection.ASCENDING

    def to_dict(self) -> Dict[str, Any]:
        """Convert sort condition to dictionary format."""
        return {
            'fieldId': self.field.field_id if isinstance(self.field, Field) else self.field,
            'direction': self.direction.value
        }


@dataclass
class QueryBuilder:
    """
    Builder pattern implementation for constructing API queries.
    
    This class helps construct complex queries with filtering,
    sorting, and pagination in a fluent interface style.
    
    Attributes:
        filters (List[FilterCondition]): List of filter conditions
        sorts (List[SortCondition]): List of sort conditions
        view_id (Optional[str]): View ID to query
        take (Optional[int]): Number of records to take
        skip (Optional[int]): Number of records to skip
        search_text (Optional[str]): Text to search for
        search_field_id (Optional[str]): Field to search in
    """
    filters: List[FilterCondition] = field(default_factory=list)
    sorts: List[SortCondition] = field(default_factory=list)
    view_id: Optional[str] = None
    take: Optional[int] = None
    skip: Optional[int] = None
    search_text: Optional[str] = None
    search_field_id: Optional[str] = None

    def filter(
        self,
        field: Union[str, Field],
        operator: Union[str, FilterOperator],
        value: Any
    ) -> 'QueryBuilder':
        """
        Add a filter condition to the query.
        
        Args:
            field: Field to filter on
            operator: Comparison operator
            value: Value to compare against
            
        Returns:
            self for method chaining
        """
        if isinstance(operator, str):
            operator = FilterOperator(operator)
        
        self.filters.append(FilterCondition(field, operator, value))
        return self

    def sort(
        self,
        field: Union[str, Field],
        direction: Union[str, SortDirection] = SortDirection.ASCENDING
    ) -> 'QueryBuilder':
        """
        Add a sort condition to the query.
        
        Args:
            field: Field to sort by
            direction: Sort direction
            
        Returns:
            self for method chaining
        """
        if isinstance(direction, str):
            direction = SortDirection(direction)
            
        self.sorts.append(SortCondition(field, direction))
        return self

    def paginate(self, take: int, skip: int = 0) -> 'QueryBuilder':
        """
        Set pagination parameters.
        
        Args:
            take: Number of records to take
            skip: Number of records to skip
            
        Returns:
            self for method chaining
        """
        self.take = take
        self.skip = skip
        return self

    def search(
        self,
        text: str,
        field: Optional[Union[str, Field]] = None
    ) -> 'QueryBuilder':
        """
        Set search parameters.
        
        Args:
            text: Text to search for
            field: Optional field to limit search to
            
        Returns:
            self for method chaining
        """
        self.search_text = text
        if field:
            self.search_field_id = (
                field.field_id if isinstance(field, Field) else field
            )
        return self

    def set_view(self, view_id: str) -> 'QueryBuilder':
        """
        Set the view to query.
        
        Args:
            view_id: ID of the view
            
        Returns:
            self for method chaining
        """
        self.view_id = view_id
        return self

    def build(self) -> Dict[str, Any]:
        """
        Build the final query parameters.
        
        Returns:
            dict: Query parameters ready for API request
        """
        params: Dict[str, Any] = {}

        if self.view_id:
            params['viewId'] = self.view_id

        if self.take is not None:
            params['take'] = self.take
        if self.skip is not None:
            params['skip'] = self.skip

        if self.filters:
            params['filter'] = [f.to_dict() for f in self.filters]

        if self.sorts:
            params['sort'] = [s.to_dict() for s in self.sorts]

        if self.search_text:
            params['search'] = [
                self.search_text,
                self.search_field_id,
                True  # Always include exact match flag
            ]

        return params


@dataclass
class View:
    """
    Represents a view in a Teable table.
    
    A view is a saved configuration of filters, sorts, and other
    display settings for a table.
    
    Attributes:
        view_id (str): Unique identifier for the view
        name (str): Display name of the view
        description (Optional[str]): View description
        filters (List[FilterCondition]): View's filter conditions
        sorts (List[SortCondition]): View's sort conditions
    """
    view_id: str
    name: str
    description: Optional[str] = None
    filters: List[FilterCondition] = field(default_factory=list)
    sorts: List[SortCondition] = field(default_factory=list)
    _client: Any = None  # Avoid circular import with TeableClient

    @classmethod
    def from_api_response(
        cls,
        data: Dict[str, Any],
        client: Any = None
    ) -> 'View':
        """
        Create a View instance from API response data.
        
        Args:
            data: Dictionary containing view data from API
            
        Returns:
            View: New view instance
        """
        # Handle filter data
        filters = []
        filter_data = data.get('filter')
        if filter_data:
            if isinstance(filter_data, list):
                for f in filter_data:
                    if isinstance(f, dict) and all(k in f for k in ['fieldId', 'operator', 'value']):
                        try:
                            filters.append(
                                FilterCondition(
                                    field=f['fieldId'],
                                    operator=FilterOperator(f['operator']),
                                    value=f['value']
                                )
                            )
                        except (ValueError, KeyError):
                            continue

        # Handle sort data
        sorts = []
        sort_data = data.get('sort')
        if sort_data:
            if isinstance(sort_data, list):
                for s in sort_data:
                    if isinstance(s, dict) and all(k in s for k in ['fieldId', 'direction']):
                        try:
                            sorts.append(
                                SortCondition(
                                    field=s['fieldId'],
                                    direction=SortDirection(s['direction'])
                                )
                            )
                        except (ValueError, KeyError):
                            continue
        
        return cls(
            view_id=data['id'],
            name=data['name'],
            description=data.get('description'),
            filters=filters,
            sorts=sorts,
            _client=client
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert view to dictionary format for API requests.
        
        Returns:
            dict: View data as dictionary
        """
        result = {
            'id': self.view_id,
            'name': self.name
        }

        if self.description:
            result['description'] = self.description

        if self.filters:
            result['filter'] = [f.to_dict() for f in self.filters]

        if self.sorts:
            result['sort'] = [s.to_dict() for s in self.sorts]

        return result

    def create_query(self) -> QueryBuilder:
        """
        Create a QueryBuilder initialized with this view's settings.
        
        Returns:
            QueryBuilder: New query builder instance
        """
        return QueryBuilder(
            filters=self.filters.copy(),
            sorts=self.sorts.copy(),
            view_id=self.view_id
        )

    def update_order(
        self,
        table_id: str,
        anchor_id: str,
        position: Position
    ) -> None:
        """
        Update this view's position relative to another view.
        
        Args:
            table_id: ID of the table containing this view
            anchor_id: ID of the view to position relative to
            position: Position relative to anchor view
            
        Raises:
            APIError: If the update fails
        """
        if not hasattr(self, '_client') or not self._client:
            raise ValueError("View instance not connected to client")
            
        self._client._make_request(
            'PUT',
            f"table/{table_id}/view/{self.view_id}/order",
            json={
                'anchorId': anchor_id,
                'position': position.value
            }
        )
