"""
Aggregation management module.

This module handles aggregation operations including row counts, group points, and field aggregations.
"""

from typing import Any, Dict, List, Optional, Union

from .http import TeableHttpClient

class AggregationManager:
    """
    Handles aggregation operations.
    
    This class manages:
    - Row count calculations
    - Group point aggregations
    - Field value aggregations
    """
    
    def __init__(self, http_client: TeableHttpClient):
        """
        Initialize the aggregation manager.
        
        Args:
            http_client: HTTP client for API communication
        """
        self._http = http_client
        
    def get_aggregations(
        self,
        table_id: str,
        *,
        view_id: Optional[str] = None,
        ignore_view_query: Optional[Union[str, bool]] = None,
        filter_by_tql: Optional[str] = None,
        filter: Optional[str] = None,
        search: Optional[List[Union[str, bool]]] = None,
        filter_link_cell_candidate: Optional[Union[List[str], str]] = None,
        filter_link_cell_selected: Optional[Union[List[str], str]] = None,
        selected_record_ids: Optional[List[str]] = None,
        group_by: Optional[str] = None,
        field: Optional[Dict[str, List[str]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get aggregations for a table with optional filtering and grouping.
        
        Args:
            table_id: ID of the table
            view_id: Optional ID of specific view to fetch
            ignore_view_query: When true, ignores the view's filter, sort, etc.
            filter_by_tql: Filter using Teable Query Language
            filter: Filter object for complex query conditions
            search: Search for records matching field and value
            filter_link_cell_candidate: Filter records that can be selected by a link cell
            filter_link_cell_selected: Filter selected records from a link cell
            selected_record_ids: Filter records by specific IDs
            group_by: Group records by specified criteria
            field: Aggregation functions to apply per field
            
        Returns:
            List[Dict[str, Any]]: List of aggregations, each containing:
                - fieldId: ID of the field
                - total: Total aggregation values
                - group: Optional grouped aggregation values
            
        Raises:
            APIError: If the request fails
        """
        params: Dict[str, Any] = {}
        
        if view_id is not None:
            params['viewId'] = view_id
        if ignore_view_query is not None:
            params['ignoreViewQuery'] = ignore_view_query
        if filter_by_tql is not None:
            params['filterByTql'] = filter_by_tql
        if filter is not None:
            params['filter'] = filter
        if search is not None:
            params['search'] = search
        if filter_link_cell_candidate is not None:
            params['filterLinkCellCandidate'] = filter_link_cell_candidate
        if filter_link_cell_selected is not None:
            params['filterLinkCellSelected'] = filter_link_cell_selected
        if selected_record_ids is not None:
            params['selectedRecordIds'] = selected_record_ids
        if group_by is not None:
            params['groupBy'] = group_by
        if field is not None:
            params['field'] = field
            
        return self._http.request(
            'GET',
            f"/table/{table_id}/aggregation",
            params=params
        )
        
    def get_row_count(
        self,
        table_id: str,
        *,
        view_id: Optional[str] = None,
        ignore_view_query: Optional[Union[str, bool]] = None,
        filter_by_tql: Optional[str] = None,
        filter: Optional[str] = None,
        search: Optional[List[Union[str, bool]]] = None,
        filter_link_cell_candidate: Optional[Union[List[str], str]] = None,
        filter_link_cell_selected: Optional[Union[List[str], str]] = None,
        selected_record_ids: Optional[List[str]] = None
    ) -> int:
        """
        Get the total number of rows in a table with optional filtering.
        
        Args:
            table_id: ID of the table
            view_id: Optional ID of specific view to fetch
            ignore_view_query: When true, ignores the view's filter, sort, etc.
            filter_by_tql: Filter using Teable Query Language
            filter: Filter object for complex query conditions
            search: Search for records matching field and value
            filter_link_cell_candidate: Filter records that can be selected by a link cell
            filter_link_cell_selected: Filter selected records from a link cell
            selected_record_ids: Filter records by specific IDs
            
        Returns:
            int: Total number of rows matching the criteria
            
        Raises:
            APIError: If the request fails
        """
        params: Dict[str, Any] = {}
        
        if view_id is not None:
            params['viewId'] = view_id
        if ignore_view_query is not None:
            params['ignoreViewQuery'] = ignore_view_query
        if filter_by_tql is not None:
            params['filterByTql'] = filter_by_tql
        if filter is not None:
            params['filter'] = filter
        if search is not None:
            params['search'] = search
        if filter_link_cell_candidate is not None:
            params['filterLinkCellCandidate'] = filter_link_cell_candidate
        if filter_link_cell_selected is not None:
            params['filterLinkCellSelected'] = filter_link_cell_selected
        if selected_record_ids is not None:
            params['selectedRecordIds'] = selected_record_ids
            
        response = self._http.request(
            'GET',
            f"/table/{table_id}/aggregation/row-count",
            params=params
        )
        return response['rowCount']
        
    def get_group_points(
        self,
        table_id: str,
        *,
        view_id: Optional[str] = None,
        filter: Optional[str] = None,
        search: Optional[List[Union[str, bool]]] = None,
        group_by: Optional[str] = None,
        collapsed_group_ids: Optional[List[str]] = None,
        ignore_view_query: Optional[Union[str, bool]] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get group points for a table.
        
        Args:
            table_id: ID of the table
            view_id: Optional ID of specific view to fetch
            filter: Filter object for complex query conditions
            search: Search for records matching field and value
            group_by: How records should be grouped
            collapsed_group_ids: Which groups are collapsed
            ignore_view_query: When true, ignores the view's filter, sort, etc.
            
        Returns:
            Optional[List[Dict[str, Any]]]: List of group points, each being either:
                Type 0 (group):
                    - id: Group ID
                    - type: 0
                    - depth: Group depth (0-2)
                    - value: Group value
                    - isCollapsed: Whether group is collapsed
                Type 1 (count):
                    - type: 1
                    - count: Number of records
            
        Raises:
            APIError: If the request fails
        """
        params: Dict[str, Any] = {}
        
        if view_id is not None:
            params['viewId'] = view_id
        if filter is not None:
            params['filter'] = filter
        if search is not None:
            params['search'] = search
        if group_by is not None:
            params['groupBy'] = group_by
        if collapsed_group_ids is not None:
            params['collapsedGroupIds'] = collapsed_group_ids
        if ignore_view_query is not None:
            params['ignoreViewQuery'] = ignore_view_query
            
        return self._http.request(
            'GET',
            f"/table/{table_id}/aggregation/group-points",
            params=params
        )
        
    def get_calendar_daily_collection(
        self,
        table_id: str,
        start_date: str,
        end_date: str,
        start_date_field_id: str,
        end_date_field_id: str,
        *,
        view_id: Optional[str] = None,
        filter: Optional[str] = None,
        search: Optional[List[Union[str, bool]]] = None,
        ignore_view_query: Optional[Union[str, bool]] = None
    ) -> Dict[str, Any]:
        """
        Get calendar daily collection for a table.
        
        Args:
            table_id: ID of the table
            start_date: Start date for the calendar range
            end_date: End date for the calendar range
            start_date_field_id: ID of the field containing start dates
            end_date_field_id: ID of the field containing end dates
            view_id: Optional ID of specific view to fetch
            filter: Optional filter object for complex query conditions
            search: Optional search for records matching field and value
            ignore_view_query: Optional flag to ignore the view's filter, sort, etc.
            
        Returns:
            Dict[str, Any]: Calendar daily collection containing:
                - countMap: Object mapping dates to record counts
                - records: List of records with their details
            
        Raises:
            APIError: If the request fails
        """
        params: Dict[str, Any] = {
            'startDate': start_date,
            'endDate': end_date,
            'startDateFieldId': start_date_field_id,
            'endDateFieldId': end_date_field_id
        }
        
        if view_id is not None:
            params['viewId'] = view_id
        if filter is not None:
            params['filter'] = filter
        if search is not None:
            params['search'] = search
        if ignore_view_query is not None:
            params['ignoreViewQuery'] = ignore_view_query
            
        return self._http.request(
            'GET',
            f"/table/{table_id}/aggregation/calendar-daily-collection",
            params=params
        )
        
    def get_search_count(
        self,
        table_id: str,
        *,
        filter: Optional[str] = None,
        view_id: Optional[str] = None,
        search: Optional[List[Union[str, bool]]] = None,
        ignore_view_query: Optional[Union[str, bool]] = None
    ) -> int:
        """
        Get count of search results in a table.
        
        Args:
            table_id: ID of the table
            filter: Optional filter object for complex query conditions
            view_id: Optional ID of specific view to fetch
            search: Optional search for records matching field and value
            ignore_view_query: Optional flag to ignore the view's filter, sort, etc.
            
        Returns:
            int: Number of records matching the search criteria
            
        Raises:
            APIError: If the request fails
        """
        params: Dict[str, Any] = {}
        
        if filter is not None:
            params['filter'] = filter
        if view_id is not None:
            params['viewId'] = view_id
        if search is not None:
            params['search'] = search
        if ignore_view_query is not None:
            params['ignoreViewQuery'] = ignore_view_query
            
        response = self._http.request(
            'GET',
            f"/table/{table_id}/aggregation/search-count",
            params=params
        )
        return response['count']
        
    def get_search_indices(
        self,
        table_id: str,
        *,
        view_id: Optional[str] = None,
        ignore_view_query: Optional[Union[str, bool]] = None,
        filter_by_tql: Optional[str] = None,
        filter: Optional[str] = None,
        search: Optional[List[Union[str, bool]]] = None,
        filter_link_cell_candidate: Optional[Union[List[str], str]] = None,
        filter_link_cell_selected: Optional[Union[List[str], str]] = None,
        selected_record_ids: Optional[List[str]] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get record indices with search query.
        
        Args:
            table_id: ID of the table
            view_id: Optional ID of specific view to fetch
            ignore_view_query: Optional flag to ignore the view's filter, sort, etc.
            filter_by_tql: Optional filter using Teable Query Language
            filter: Optional filter object for complex query conditions
            search: Optional search for records matching field and value
            filter_link_cell_candidate: Optional filter for records that can be selected by a link cell
            filter_link_cell_selected: Optional filter for selected records from a link cell
            selected_record_ids: Optional filter for specific record IDs
            
        Returns:
            Optional[List[Dict[str, Any]]]: List of index/field pairs, each containing:
                - index: Record index number
                - fieldId: ID of the field
            
        Raises:
            APIError: If the request fails
        """
        params: Dict[str, Any] = {}
        
        if view_id is not None:
            params['viewId'] = view_id
        if ignore_view_query is not None:
            params['ignoreViewQuery'] = ignore_view_query
        if filter_by_tql is not None:
            params['filterByTql'] = filter_by_tql
        if filter is not None:
            params['filter'] = filter
        if search is not None:
            params['search'] = search
        if filter_link_cell_candidate is not None:
            params['filterLinkCellCandidate'] = filter_link_cell_candidate
        if filter_link_cell_selected is not None:
            params['filterLinkCellSelected'] = filter_link_cell_selected
        if selected_record_ids is not None:
            params['selectedRecordIds'] = selected_record_ids
            
        return self._http.request(
            'GET',
            f"/table/{table_id}/aggregation/search-index",
            params=params
        )
