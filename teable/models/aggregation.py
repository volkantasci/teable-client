"""Aggregation Model Module

This module provides the Aggregation class for representing
aggregation data returned by the API.
"""

from dataclasses import dataclass
from enum import Enum
from enum import IntEnum
from datetime import datetime
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union


@dataclass
class SearchIndex:
    """
    Represents a search result index.
    
    Attributes:
        index: Index of the result
        field_id: ID of the field
    """
    
    index: int
    field_id: str
    
    @classmethod
    def from_api_response(cls, response: dict) -> 'SearchIndex':
        """
        Create a SearchIndex instance from API response data.
        
        Args:
            response: API response dictionary
            
        Returns:
            SearchIndex: Created instance
        """
        return cls(
            index=response['index'],
            field_id=response['fieldId']
        )


class GroupPointType(IntEnum):
    """Enumeration of group point types."""
    
    GROUP = 0
    COUNT = 1


class AggregationFunction(str, Enum):
    """Enumeration of available aggregation functions."""
    
    COUNT = 'count'
    EMPTY = 'empty'
    FILLED = 'filled'
    UNIQUE = 'unique'
    MAX = 'max'
    MIN = 'min'
    SUM = 'sum'
    AVERAGE = 'average'
    CHECKED = 'checked'
    UNCHECKED = 'unChecked'
    PERCENT_EMPTY = 'percentEmpty'
    PERCENT_FILLED = 'percentFilled'
    PERCENT_UNIQUE = 'percentUnique'
    PERCENT_CHECKED = 'percentChecked'
    PERCENT_UNCHECKED = 'percentUnChecked'
    EARLIEST_DATE = 'earliestDate'
    LATEST_DATE = 'latestDate'
    DATE_RANGE_DAYS = 'dateRangeOfDays'
    DATE_RANGE_MONTHS = 'dateRangeOfMonths'
    TOTAL_ATTACHMENT_SIZE = 'totalAttachmentSize'


@dataclass
class CalendarRecord:
    """
    Represents a record in a calendar view.
    
    Attributes:
        id: Record ID
        fields: Field values
        name: Optional primary field value
        auto_number: Optional auto number
        created_time: Optional creation time
        last_modified_time: Optional last modification time
        created_by: Optional creator name
        last_modified_by: Optional last modifier name
    """
    
    id: str
    fields: Dict[str, Any]
    name: Optional[str] = None
    auto_number: Optional[int] = None
    created_time: Optional[datetime] = None
    last_modified_time: Optional[datetime] = None
    created_by: Optional[str] = None
    last_modified_by: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, response: dict) -> 'CalendarRecord':
        """
        Create a CalendarRecord instance from API response data.
        
        Args:
            response: API response dictionary
            
        Returns:
            CalendarRecord: Created instance
        """
        return cls(
            id=response['id'],
            fields=response['fields'],
            name=response.get('name'),
            auto_number=response.get('autoNumber'),
            created_time=datetime.fromisoformat(response['createdTime']) if response.get('createdTime') else None,
            last_modified_time=datetime.fromisoformat(response['lastModifiedTime']) if response.get('lastModifiedTime') else None,
            created_by=response.get('createdBy'),
            last_modified_by=response.get('lastModifiedBy')
        )


@dataclass
class CalendarDailyCollection:
    """
    Represents a collection of calendar records grouped by day.
    
    Attributes:
        count_map: Mapping of dates to record counts
        records: List of calendar records
    """
    
    count_map: Dict[str, int]
    records: List[CalendarRecord]
    
    @classmethod
    def from_api_response(cls, response: dict) -> 'CalendarDailyCollection':
        """
        Create a CalendarDailyCollection instance from API response data.
        
        Args:
            response: API response dictionary
            
        Returns:
            CalendarDailyCollection: Created instance
        """
        return cls(
            count_map=response['countMap'],
            records=[CalendarRecord.from_api_response(r) for r in response['records']]
        )


@dataclass
class GroupPoint:
    """
    Represents a group point in a table view.
    
    Attributes:
        type: Type of group point (GROUP or COUNT)
        id: Optional ID of the group
        depth: Optional depth of the group (0-2)
        value: Optional value of the group
        is_collapsed: Optional flag indicating if group is collapsed
        count: Optional count for COUNT type points
    """
    
    type: GroupPointType
    id: Optional[str] = None
    depth: Optional[int] = None
    value: Optional[Any] = None
    is_collapsed: Optional[bool] = None
    count: Optional[int] = None
    
    @classmethod
    def from_api_response(cls, response: dict) -> 'GroupPoint':
        """
        Create a GroupPoint instance from API response data.
        
        Args:
            response: API response dictionary
            
        Returns:
            GroupPoint: Created instance
        """
        point_type = GroupPointType(response['type'])
        
        if point_type == GroupPointType.GROUP:
            return cls(
                type=point_type,
                id=response['id'],
                depth=response['depth'],
                value=response.get('value'),
                is_collapsed=response['isCollapsed']
            )
        else:  # COUNT
            return cls(
                type=point_type,
                count=response['count']
            )


@dataclass
class AggregationValue:
    """
    Represents an aggregation value with its function.
    
    Attributes:
        value: The aggregated value
        agg_func: The aggregation function used
    """
    
    value: Optional[Any]
    agg_func: AggregationFunction
    
    @classmethod
    def from_api_response(cls, response: dict) -> 'AggregationValue':
        """
        Create an AggregationValue instance from API response data.
        
        Args:
            response: API response dictionary
            
        Returns:
            AggregationValue: Created instance
        """
        return cls(
            value=response['value'],
            agg_func=AggregationFunction(response['aggFunc'])
        )


@dataclass
class FieldAggregation:
    """
    Represents aggregations for a field.
    
    Attributes:
        field_id: ID of the field
        total: Overall aggregation for the field
        group: Optional group-wise aggregations
    """
    
    field_id: str
    total: AggregationValue
    group: Optional[Dict[str, AggregationValue]] = None
    
    @classmethod
    def from_api_response(cls, response: dict) -> 'FieldAggregation':
        """
        Create a FieldAggregation instance from API response data.
        
        Args:
            response: API response dictionary
            
        Returns:
            FieldAggregation: Created instance
        """
        group = None
        if response.get('group'):
            group = {
                k: AggregationValue.from_api_response(v)
                for k, v in response['group'].items()
            }
            
        return cls(
            field_id=response['fieldId'],
            total=AggregationValue.from_api_response(response['total']),
            group=group
        )


@dataclass
class Aggregation:
    """
    Represents a collection of field aggregations.
    
    Attributes:
        aggregations: List of field aggregations
    """
    
    aggregations: List[FieldAggregation]
    
    @classmethod
    def from_api_response(cls, response: dict) -> 'Aggregation':
        """
        Create an Aggregation instance from API response data.
        
        Args:
            response: API response dictionary
            
        Returns:
            Aggregation: Created instance
        """
        return cls(
            aggregations=[
                FieldAggregation.from_api_response(a)
                for a in response['aggregations']
            ]
        )
