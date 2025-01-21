"""
Selection management module.

This module handles selection operations including copying, pasting, and range selection.
"""

from typing import Any, Dict, List, Optional, Union, Literal

from ..models.selection import SelectionRange
from .http import TeableHttpClient

class SelectionManager:
    """
    Handles selection operations.
    
    This class manages:
    - Selection range operations
    - Copy/paste operations
    - Selection clearing
    - Selection status
    """
    
    def __init__(self, http_client: TeableHttpClient):
        """
        Initialize the selection manager.
        
        Args:
            http_client: HTTP client for API communication
        """
        self._http = http_client
        
    def get_selection_range_to_id(
        self,
        table_id: str,
        ranges: str,
        return_type: Literal['recordId', 'fieldId', 'all'],
        view_id: Optional[str] = None,
        ignore_view_query: Optional[bool] = None,
        filter_by_tql: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None,
        search: Optional[List[Any]] = None,
        filter_link_cell_candidate: Optional[Union[str, List[str]]] = None,
        filter_link_cell_selected: Optional[Union[str, List[str]]] = None,
        selected_record_ids: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        group_by: Optional[str] = None,
        collapsed_group_ids: Optional[List[str]] = None,
        exclude_field_ids: Optional[List[str]] = None,
        selection_type: Optional[Literal['rows', 'columns']] = None
    ) -> SelectionRange:
        """
        Get the ID of records and fields from the selected range.
        
        Args:
            table_id: ID of the table
            ranges: Coordinates [column, row][] of selected range
            return_type: Type of IDs to return ('recordId', 'fieldId', 'all')
            view_id: Optional view ID to filter by
            ignore_view_query: Whether to ignore view's filter/sort
            filter_by_tql: Filter using Teable Query Language
            filter: Filter object for complex queries
            search: Search parameters [value, field, exact]
            filter_link_cell_candidate: Filter by link cell candidates
            filter_link_cell_selected: Filter by link cell selection
            selected_record_ids: Filter by specific record IDs
            order_by: Sort specification
            group_by: Group specification
            collapsed_group_ids: List of collapsed group IDs
            exclude_field_ids: List of field IDs to exclude
            selection_type: Type of non-contiguous selections
            
        Returns:
            SelectionRange: Selection range information
            
        Raises:
            APIError: If the request fails
        """
        params: Dict[str, Any] = {
            'ranges': ranges,
            'returnType': return_type
        }
        if view_id:
            params['viewId'] = view_id
        if ignore_view_query is not None:
            params['ignoreViewQuery'] = ignore_view_query
        if filter_by_tql:
            params['filterByTql'] = filter_by_tql
        if filter:
            params['filter'] = filter
        if search:
            params['search'] = search
        if filter_link_cell_candidate:
            params['filterLinkCellCandidate'] = filter_link_cell_candidate
        if filter_link_cell_selected:
            params['filterLinkCellSelected'] = filter_link_cell_selected
        if selected_record_ids:
            params['selectedRecordIds'] = selected_record_ids
        if order_by:
            params['orderBy'] = order_by
        if group_by:
            params['groupBy'] = group_by
        if collapsed_group_ids:
            params['collapsedGroupIds'] = collapsed_group_ids
        if exclude_field_ids:
            params['excludeFieldIds'] = exclude_field_ids
        if selection_type:
            params['type'] = selection_type
            
        response = self._http.request(
            'GET',
            f"table/{table_id}/selection/range-to-id",
            params=params
        )
        return SelectionRange.from_api_response(response)
        
    def clear_selection(
        self,
        table_id: str,
        ranges: List[List[int]],
        view_id: Optional[str] = None,
        ignore_view_query: Optional[bool] = None,
        filter_by_tql: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None,
        search: Optional[List[Any]] = None,
        filter_link_cell_candidate: Optional[Union[str, List[str]]] = None,
        filter_link_cell_selected: Optional[Union[str, List[str]]] = None,
        selected_record_ids: Optional[List[str]] = None,
        order_by: Optional[List[Dict[str, Any]]] = None,
        group_by: Optional[List[Dict[str, str]]] = None,
        collapsed_group_ids: Optional[List[str]] = None,
        exclude_field_ids: Optional[List[str]] = None,
        selection_type: Optional[Literal['rows', 'columns']] = None
    ) -> bool:
        """
        Clear the selection range.
        
        Args:
            table_id: ID of the table
            ranges: Coordinates [column, row][] of selected range
            view_id: Optional view ID to filter by
            ignore_view_query: Whether to ignore view's filter/sort
            filter_by_tql: Filter using Teable Query Language
            filter: Filter object for complex queries
            search: Search parameters [value, field, exact]
            filter_link_cell_candidate: Filter by link cell candidates
            filter_link_cell_selected: Filter by link cell selection
            selected_record_ids: Filter by specific record IDs
            order_by: Sort specification
            group_by: Group specification
            collapsed_group_ids: List of collapsed group IDs
            exclude_field_ids: List of field IDs to exclude
            selection_type: Type of non-contiguous selections
            
        Returns:
            bool: True if successful
            
        Raises:
            APIError: If the request fails
        """
        data: Dict[str, Any] = {
            'ranges': ranges
        }
        if view_id:
            data['viewId'] = view_id
        if ignore_view_query is not None:
            data['ignoreViewQuery'] = ignore_view_query
        if filter_by_tql:
            data['filterByTql'] = filter_by_tql
        if filter:
            data['filter'] = filter
        if search:
            data['search'] = search
        if filter_link_cell_candidate:
            data['filterLinkCellCandidate'] = filter_link_cell_candidate
        if filter_link_cell_selected:
            data['filterLinkCellSelected'] = filter_link_cell_selected
        if selected_record_ids:
            data['selectedRecordIds'] = selected_record_ids
        if order_by:
            data['orderBy'] = order_by
        if group_by:
            data['groupBy'] = group_by
        if collapsed_group_ids:
            data['collapsedGroupIds'] = collapsed_group_ids
        if exclude_field_ids:
            data['excludeFieldIds'] = exclude_field_ids
        if selection_type:
            data['type'] = selection_type
            
        self._http.request(
            'PATCH',
            f"table/{table_id}/selection/clear",
            json=data
        )
        return True
        
    def get_selection_copy(
        self,
        table_id: str,
        ranges: str,
        view_id: Optional[str] = None,
        ignore_view_query: Optional[bool] = None,
        filter_by_tql: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None,
        search: Optional[List[Any]] = None,
        filter_link_cell_candidate: Optional[Union[str, List[str]]] = None,
        filter_link_cell_selected: Optional[Union[str, List[str]]] = None,
        selected_record_ids: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        group_by: Optional[str] = None,
        collapsed_group_ids: Optional[List[str]] = None,
        exclude_field_ids: Optional[List[str]] = None,
        selection_type: Optional[Literal['rows', 'columns']] = None
    ) -> Dict[str, Any]:
        """
        Get copy content from selection range.
        
        Args:
            table_id: ID of the table
            ranges: Coordinates [column, row][] of selected range
            view_id: Optional view ID to filter by
            ignore_view_query: Whether to ignore view's filter/sort
            filter_by_tql: Filter using Teable Query Language
            filter: Filter object for complex queries
            search: Search parameters [value, field, exact]
            filter_link_cell_candidate: Filter by link cell candidates
            filter_link_cell_selected: Filter by link cell selection
            selected_record_ids: Filter by specific record IDs
            order_by: Sort specification
            group_by: Group specification
            collapsed_group_ids: List of collapsed group IDs
            exclude_field_ids: List of field IDs to exclude
            selection_type: Type of non-contiguous selections
            
        Returns:
            Dict[str, Any]: Copy content and header information
            
        Raises:
            APIError: If the request fails
        """
        params: Dict[str, Any] = {
            'ranges': ranges
        }
        if view_id:
            params['viewId'] = view_id
        if ignore_view_query is not None:
            params['ignoreViewQuery'] = ignore_view_query
        if filter_by_tql:
            params['filterByTql'] = filter_by_tql
        if filter:
            params['filter'] = filter
        if search:
            params['search'] = search
        if filter_link_cell_candidate:
            params['filterLinkCellCandidate'] = filter_link_cell_candidate
        if filter_link_cell_selected:
            params['filterLinkCellSelected'] = filter_link_cell_selected
        if selected_record_ids:
            params['selectedRecordIds'] = selected_record_ids
        if order_by:
            params['orderBy'] = order_by
        if group_by:
            params['groupBy'] = group_by
        if collapsed_group_ids:
            params['collapsedGroupIds'] = collapsed_group_ids
        if exclude_field_ids:
            params['excludeFieldIds'] = exclude_field_ids
        if selection_type:
            params['type'] = selection_type
            
        return self._http.request(
            'GET',
            f"table/{table_id}/selection/copy",
            params=params
        )
        
    def paste_selection(
        self,
        table_id: str,
        ranges: List[List[int]],
        content: str,
        header: Optional[List[Dict[str, Any]]] = None,
        view_id: Optional[str] = None,
        ignore_view_query: Optional[bool] = None,
        filter_by_tql: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None,
        search: Optional[List[Any]] = None,
        filter_link_cell_candidate: Optional[Union[str, List[str]]] = None,
        filter_link_cell_selected: Optional[Union[str, List[str]]] = None,
        selected_record_ids: Optional[List[str]] = None,
        order_by: Optional[List[Dict[str, Any]]] = None,
        group_by: Optional[List[Dict[str, str]]] = None,
        collapsed_group_ids: Optional[List[str]] = None,
        exclude_field_ids: Optional[List[str]] = None,
        selection_type: Optional[Literal['rows', 'columns']] = None
    ) -> Dict[str, List[List[int]]]:
        """
        Paste content into selection range.
        
        Args:
            table_id: ID of the table
            ranges: Coordinates [column, row][] of selected range
            content: Content to paste
            header: Optional table header for paste operation
            view_id: Optional view ID to filter by
            ignore_view_query: Whether to ignore view's filter/sort
            filter_by_tql: Filter using Teable Query Language
            filter: Filter object for complex queries
            search: Search parameters [value, field, exact]
            filter_link_cell_candidate: Filter by link cell candidates
            filter_link_cell_selected: Filter by link cell selection
            selected_record_ids: Filter by specific record IDs
            order_by: Sort specification
            group_by: Group specification
            collapsed_group_ids: List of collapsed group IDs
            exclude_field_ids: List of field IDs to exclude
            selection_type: Type of non-contiguous selections
            
        Returns:
            Dict[str, List[List[int]]]: Updated ranges after paste
            
        Raises:
            APIError: If the request fails
        """
        data: Dict[str, Any] = {
            'ranges': ranges,
            'content': content
        }
        if header is not None:
            data['header'] = header
        if view_id:
            data['viewId'] = view_id
        if ignore_view_query is not None:
            data['ignoreViewQuery'] = ignore_view_query
        if filter_by_tql:
            data['filterByTql'] = filter_by_tql
        if filter:
            data['filter'] = filter
        if search:
            data['search'] = search
        if filter_link_cell_candidate:
            data['filterLinkCellCandidate'] = filter_link_cell_candidate
        if filter_link_cell_selected:
            data['filterLinkCellSelected'] = filter_link_cell_selected
        if selected_record_ids:
            data['selectedRecordIds'] = selected_record_ids
        if order_by:
            data['orderBy'] = order_by
        if group_by:
            data['groupBy'] = group_by
        if collapsed_group_ids:
            data['collapsedGroupIds'] = collapsed_group_ids
        if exclude_field_ids:
            data['excludeFieldIds'] = exclude_field_ids
        if selection_type:
            data['type'] = selection_type
            
        return self._http.request(
            'PATCH',
            f"table/{table_id}/selection/paste",
            json=data
        )
        
    def delete_selection(
        self,
        table_id: str,
        ranges: str,
        view_id: Optional[str] = None,
        ignore_view_query: Optional[bool] = None,
        filter_by_tql: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None,
        search: Optional[List[Any]] = None,
        filter_link_cell_candidate: Optional[Union[str, List[str]]] = None,
        filter_link_cell_selected: Optional[Union[str, List[str]]] = None,
        selected_record_ids: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        group_by: Optional[str] = None,
        collapsed_group_ids: Optional[List[str]] = None,
        exclude_field_ids: Optional[List[str]] = None,
        selection_type: Optional[Literal['rows', 'columns']] = None
    ) -> Dict[str, List[str]]:
        """
        Delete the selected data.
        
        Args:
            table_id: ID of the table
            ranges: Coordinates [column, row][] of selected range
            view_id: Optional view ID to filter by
            ignore_view_query: Whether to ignore view's filter/sort
            filter_by_tql: Filter using Teable Query Language
            filter: Filter object for complex queries
            search: Search parameters [value, field, exact]
            filter_link_cell_candidate: Filter by link cell candidates
            filter_link_cell_selected: Filter by link cell selection
            selected_record_ids: Filter by specific record IDs
            order_by: Sort specification
            group_by: Group specification
            collapsed_group_ids: List of collapsed group IDs
            exclude_field_ids: List of field IDs to exclude
            selection_type: Type of non-contiguous selections
            
        Returns:
            Dict[str, List[str]]: IDs of deleted records
            
        Raises:
            APIError: If the request fails
        """
        params: Dict[str, Any] = {
            'ranges': ranges
        }
        if view_id:
            params['viewId'] = view_id
        if ignore_view_query is not None:
            params['ignoreViewQuery'] = ignore_view_query
        if filter_by_tql:
            params['filterByTql'] = filter_by_tql
        if filter:
            params['filter'] = filter
        if search:
            params['search'] = search
        if filter_link_cell_candidate:
            params['filterLinkCellCandidate'] = filter_link_cell_candidate
        if filter_link_cell_selected:
            params['filterLinkCellSelected'] = filter_link_cell_selected
        if selected_record_ids:
            params['selectedRecordIds'] = selected_record_ids
        if order_by:
            params['orderBy'] = order_by
        if group_by:
            params['groupBy'] = group_by
        if collapsed_group_ids:
            params['collapsedGroupIds'] = collapsed_group_ids
        if exclude_field_ids:
            params['excludeFieldIds'] = exclude_field_ids
        if selection_type:
            params['type'] = selection_type
            
        return self._http.request(
            'DELETE',
            f"table/{table_id}/selection/delete",
            params=params
        )
        
    def temporary_paste(
        self,
        table_id: str,
        ranges: List[List[int]],
        content: str,
        view_id: Optional[str] = None,
        exclude_field_ids: Optional[List[str]] = None,
        ignore_view_query: Optional[bool] = None,
        header: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Dict[str, Any]]]:
        """
        Paste operation for pre-filled table rows.
        
        Args:
            table_id: ID of the table
            ranges: Coordinates [column, row][] of selected range
            content: Content to paste
            view_id: Optional view ID to filter by
            exclude_field_ids: Optional list of field IDs to exclude
            ignore_view_query: Whether to ignore view's filter/sort
            header: Optional table header for paste operation
            
        Returns:
            List[Dict[str, Dict[str, Any]]]: List of pre-filled records
            
        Raises:
            APIError: If the request fails
        """
        data: Dict[str, Any] = {
            'ranges': ranges,
            'content': content
        }
        if view_id:
            data['viewId'] = view_id
        if exclude_field_ids:
            data['excludeFieldIds'] = exclude_field_ids
        if ignore_view_query is not None:
            data['ignoreViewQuery'] = ignore_view_query
        if header is not None:
            data['header'] = header
            
        return self._http.request(
            'PATCH',
            f"table/{table_id}/selection/temporaryPaste",
            json=data
        )
