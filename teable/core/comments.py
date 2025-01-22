"""
Comment management module.

This module handles operations for managing comments and reactions.
"""

from typing import Any, Dict, List, Literal, Optional, TypedDict, Union, cast

CellFormat = Literal['json', 'text']
FieldKeyType = Literal['id', 'name']

ListDirection = Literal['forward', 'backward']

NodeType = Literal['p', 'span', 'mention', 'a', 'img']

class SpanNode(TypedDict):
    """Type definition for span node."""
    type: Literal['span']
    value: str

class MentionNode(TypedDict, total=False):
    """Type definition for mention node."""
    type: Literal['mention']
    value: str
    name: Optional[str]
    avatar: Optional[str]

class LinkNode(TypedDict):
    """Type definition for link node."""
    type: Literal['a']
    value: Optional[str]
    url: str
    title: str

class ImageNode(TypedDict, total=False):
    """Type definition for image node."""
    type: Literal['img']
    value: Optional[str]
    path: str
    width: Optional[float]
    url: Optional[str]

class ParagraphNode(TypedDict):
    """Type definition for paragraph node."""
    type: Literal['p']
    value: Optional[str]
    children: List[Union[SpanNode, MentionNode, LinkNode]]

ContentNode = Union[ParagraphNode, ImageNode]

class CommentUser(TypedDict, total=False):
    """Type definition for comment user."""
    id: str
    name: str
    avatar: Optional[str]

class CommentReaction(TypedDict):
    """Type definition for comment reaction."""
    reaction: str
    user: List[CommentUser]

class Comment(TypedDict, total=False):
    """Type definition for comment response."""
    id: str
    content: List[ContentNode]
    createdBy: CommentUser
    reaction: Optional[List[CommentReaction]]
    createdTime: str
    lastModifiedTime: Optional[str]
    quoteId: Optional[str]
    deletedTime: Optional[str]

from .http import TeableHttpClient

class CreateCommentRequest(TypedDict, total=False):
    """Type definition for create comment request."""
    content: List[ContentNode]
    quoteId: Optional[str]

class UpdateCommentRequest(TypedDict):
    """Type definition for update comment request."""
    content: List[ContentNode]

class ReactionRequest(TypedDict):
    """Type definition for reaction request."""
    reaction: str

class CommentSubscription(TypedDict):
    """Type definition for comment subscription response."""
    tableId: str
    recordId: str
    createdBy: str

class CommentCountTotal(TypedDict):
    """Type definition for comment count total response."""
    count: int

class CommentCount(TypedDict):
    """Type definition for comment count response."""
    recordId: str
    count: int

class CommentListResponse(TypedDict):
    """Type definition for comment list response."""
    comments: List[Comment]
    nextCursor: Optional[str]

class CommentManager:
    """
    Handles comment operations.
    
    This class manages:
    - Comment reactions
    """
    
    def __init__(self, http_client: TeableHttpClient):
        """
        Initialize the comment manager.
        
        Args:
            http_client: HTTP client for API communication
        """
        self._http = http_client
        
    def create_reaction(
        self,
        table_id: str,
        record_id: str,
        comment_id: str,
        reaction: str
    ) -> bool:
        """
        Create a reaction on a comment.
        
        Args:
            table_id: ID of the table
            record_id: ID of the record
            comment_id: ID of the comment
            reaction: Reaction to add
            
        Returns:
            bool: True if creation successful
            
        Raises:
            APIError: If the creation fails
        """
        data: ReactionRequest = {
            'reaction': reaction
        }
        
        self._http.request(
            'POST',
            f"/comment/{table_id}/{record_id}/{comment_id}/reaction",
            json=data
        )
        return True
        
    def get_total_comment_count(
        self,
        table_id: str,
        *,
        projection: Optional[List[str]] = None,
        cell_format: Optional[CellFormat] = None,
        field_key_type: Optional[FieldKeyType] = None,
        view_id: Optional[str] = None,
        ignore_view_query: Optional[bool] = None,
        filter_by_tql: Optional[str] = None,
        filter: Optional[str] = None,
        search: Optional[List[str]] = None,
        filter_link_cell_candidate: Optional[Union[List[str], str]] = None,
        filter_link_cell_selected: Optional[Union[List[str], str]] = None,
        selected_record_ids: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        group_by: Optional[str] = None,
        collapsed_group_ids: Optional[List[str]] = None,
        take: Optional[Union[int, str]] = None,
        skip: Optional[Union[int, str]] = None
    ) -> CommentCountTotal:
        """
        Get total comment count for records in a table.
        
        Args:
            table_id: ID of the table
            projection: Optional list of fields to include
            cell_format: Optional format for cell values ('json' or 'text')
            field_key_type: Optional key type for fields ('id' or 'name')
            view_id: Optional ID of view to use
            ignore_view_query: Optional flag to ignore view query
            filter_by_tql: Optional TQL filter string
            filter: Optional filter string
            search: Optional search parameters
            filter_link_cell_candidate: Optional link cell candidate filter
            filter_link_cell_selected: Optional link cell selected filter
            selected_record_ids: Optional list of record IDs to filter by
            order_by: Optional order by string
            group_by: Optional group by string
            collapsed_group_ids: Optional list of collapsed group IDs
            take: Optional number of records to take (max 2000)
            skip: Optional number of records to skip
            
        Returns:
            CommentCountTotal: Total comment count
            
        Raises:
            APIError: If the request fails
            ValueError: If take exceeds 2000
        """
        if take is not None and int(take) > 2000:
            raise ValueError("take cannot exceed 2000")
            
        params: Dict[str, Any] = {}
        if projection is not None:
            params['projection'] = projection
        if cell_format is not None:
            params['cellFormat'] = cell_format
        if field_key_type is not None:
            params['fieldKeyType'] = field_key_type
        if view_id is not None:
            params['viewId'] = view_id
        if ignore_view_query is not None:
            params['ignoreViewQuery'] = str(ignore_view_query).lower()
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
        if order_by is not None:
            params['orderBy'] = order_by
        if group_by is not None:
            params['groupBy'] = group_by
        if collapsed_group_ids is not None:
            params['collapsedGroupIds'] = collapsed_group_ids
        if take is not None:
            params['take'] = take
        if skip is not None:
            params['skip'] = skip
            
        return cast(
            CommentCountTotal,
            self._http.request(
                'GET',
                f"/comment/{table_id}/count",
                params=params
            )
        )
        
    def get_comment_counts(
        self,
        table_id: str,
        *,
        projection: Optional[List[str]] = None,
        cell_format: Optional[CellFormat] = None,
        field_key_type: Optional[FieldKeyType] = None,
        view_id: Optional[str] = None,
        ignore_view_query: Optional[bool] = None,
        filter_by_tql: Optional[str] = None,
        filter: Optional[str] = None,
        search: Optional[List[str]] = None,
        filter_link_cell_candidate: Optional[Union[List[str], str]] = None,
        filter_link_cell_selected: Optional[Union[List[str], str]] = None,
        selected_record_ids: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        group_by: Optional[str] = None,
        collapsed_group_ids: Optional[List[str]] = None,
        take: Optional[Union[int, str]] = None,
        skip: Optional[Union[int, str]] = None
    ) -> List[CommentCount]:
        """
        Get comment counts for records in a table.
        
        Args:
            table_id: ID of the table
            projection: Optional list of fields to include
            cell_format: Optional format for cell values ('json' or 'text')
            field_key_type: Optional key type for fields ('id' or 'name')
            view_id: Optional ID of view to use
            ignore_view_query: Optional flag to ignore view query
            filter_by_tql: Optional TQL filter string
            filter: Optional filter string
            search: Optional search parameters
            filter_link_cell_candidate: Optional link cell candidate filter
            filter_link_cell_selected: Optional link cell selected filter
            selected_record_ids: Optional list of record IDs to filter by
            order_by: Optional order by string
            group_by: Optional group by string
            collapsed_group_ids: Optional list of collapsed group IDs
            take: Optional number of records to take (max 2000)
            skip: Optional number of records to skip
            
        Returns:
            List[CommentCount]: List of comment counts by record
            
        Raises:
            APIError: If the request fails
            ValueError: If take exceeds 2000
        """
        if take is not None and int(take) > 2000:
            raise ValueError("take cannot exceed 2000")
            
        params: Dict[str, Any] = {}
        if projection is not None:
            params['projection'] = projection
        if cell_format is not None:
            params['cellFormat'] = cell_format
        if field_key_type is not None:
            params['fieldKeyType'] = field_key_type
        if view_id is not None:
            params['viewId'] = view_id
        if ignore_view_query is not None:
            params['ignoreViewQuery'] = str(ignore_view_query).lower()
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
        if order_by is not None:
            params['orderBy'] = order_by
        if group_by is not None:
            params['groupBy'] = group_by
        if collapsed_group_ids is not None:
            params['collapsedGroupIds'] = collapsed_group_ids
        if take is not None:
            params['take'] = take
        if skip is not None:
            params['skip'] = skip
            
        return cast(
            List[CommentCount],
            self._http.request(
                'GET',
                f"/comment/{table_id}/count",
                params=params
            )
        )
        
    def get_attachment_url(
        self,
        table_id: str,
        record_id: str,
        path: str
    ) -> str:
        """
        Get URL for a comment attachment.
        
        Args:
            table_id: ID of the table
            record_id: ID of the record
            path: Path of the attachment
            
        Returns:
            str: URL of the attachment
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(
            'GET',
            f"/comment/{table_id}/{record_id}/attachment/{path}"
        )
        
    def get_subscription(
        self,
        table_id: str,
        record_id: str
    ) -> Optional[CommentSubscription]:
        """
        Get subscription details for record comments.
        
        Args:
            table_id: ID of the table
            record_id: ID of the record
            
        Returns:
            Optional[CommentSubscription]: Subscription information if exists, None otherwise
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(
            'GET',
            f"/comment/{table_id}/{record_id}/subscribe"
        )
        
    def subscribe(
        self,
        table_id: str,
        record_id: str
    ) -> bool:
        """
        Subscribe to record comments.
        
        Args:
            table_id: ID of the table
            record_id: ID of the record
            
        Returns:
            bool: True if subscription successful
            
        Raises:
            APIError: If the subscription fails
        """
        self._http.request(
            'POST',
            f"/comment/{table_id}/{record_id}/subscribe"
        )
        return True
        
    def unsubscribe(
        self,
        table_id: str,
        record_id: str
    ) -> bool:
        """
        Unsubscribe from record comments.
        
        Args:
            table_id: ID of the table
            record_id: ID of the record
            
        Returns:
            bool: True if unsubscription successful
            
        Raises:
            APIError: If the unsubscription fails
        """
        self._http.request(
            'DELETE',
            f"/comment/{table_id}/{record_id}/subscribe"
        )
        return True
        
    def create_comment(
        self,
        table_id: str,
        record_id: str,
        content: List[ContentNode],
        quote_id: Optional[str] = None
    ) -> bool:
        """
        Create a new comment on a record.
        
        Args:
            table_id: ID of the table
            record_id: ID of the record
            content: Comment content
            quote_id: Optional ID of comment being quoted
            
        Returns:
            bool: True if creation successful
            
        Raises:
            APIError: If the creation fails
        """
        data: CreateCommentRequest = {
            'content': content
        }
        
        if quote_id is not None:
            data['quoteId'] = quote_id
            
        self._http.request(
            'POST',
            f"/comment/{table_id}/{record_id}/create",
            json=data
        )
        return True
        
    def list_comments(
        self,
        table_id: str,
        record_id: str,
        *,
        take: Optional[Union[int, str]] = None,
        cursor: Optional[str] = None,
        include_cursor: Optional[bool] = None,
        direction: Optional[ListDirection] = None
    ) -> CommentListResponse:
        """
        Get list of comments for a record.
        
        Args:
            table_id: ID of the table
            record_id: ID of the record
            take: Optional number of comments to return (max 1000)
            cursor: Optional cursor for pagination
            include_cursor: Optional flag to include cursor item
            direction: Optional list direction ('forward' or 'backward')
            
        Returns:
            CommentListResponse: List response including:
                - comments: List of comments
                - nextCursor: Optional cursor for next page
            
        Raises:
            APIError: If the request fails
            ValueError: If take exceeds 1000
        """
        if take is not None and int(take) > 1000:
            raise ValueError("take cannot exceed 1000")
            
        params: Dict[str, Any] = {}
        if take is not None:
            params['take'] = take
        if cursor is not None:
            params['cursor'] = cursor
        if include_cursor is not None:
            params['includeCursor'] = str(include_cursor).lower()
        if direction is not None:
            params['direction'] = direction
            
        return self._http.request(
            'GET',
            f"/comment/{table_id}/{record_id}/list",
            params=params
        )
        
    def get_comment(
        self,
        table_id: str,
        record_id: str,
        comment_id: str
    ) -> Comment:
        """
        Get details of a comment.
        
        Args:
            table_id: ID of the table
            record_id: ID of the record
            comment_id: ID of the comment
            
        Returns:
            Comment: Comment information including:
                - Basic info (id, content)
                - Creator information
                - Reactions
                - Timestamps
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(
            'GET',
            f"/comment/{table_id}/{record_id}/{comment_id}"
        )
        
    def update_comment(
        self,
        table_id: str,
        record_id: str,
        comment_id: str,
        content: List[ContentNode]
    ) -> bool:
        """
        Update a comment.
        
        Args:
            table_id: ID of the table
            record_id: ID of the record
            comment_id: ID of the comment
            content: New comment content
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        data: UpdateCommentRequest = {
            'content': content
        }
        
        self._http.request(
            'PATCH',
            f"/comment/{table_id}/{record_id}/{comment_id}",
            json=data
        )
        return True
        
    def delete_comment(
        self,
        table_id: str,
        record_id: str,
        comment_id: str
    ) -> bool:
        """
        Delete a comment.
        
        Args:
            table_id: ID of the table
            record_id: ID of the record
            comment_id: ID of the comment
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            APIError: If the deletion fails
        """
        self._http.request(
            'DELETE',
            f"/comment/{table_id}/{record_id}/{comment_id}"
        )
        return True
        
    def delete_reaction(
        self,
        table_id: str,
        record_id: str,
        comment_id: str,
        reaction: str
    ) -> bool:
        """
        Delete a reaction from a comment.
        
        Args:
            table_id: ID of the table
            record_id: ID of the record
            comment_id: ID of the comment
            reaction: Reaction to remove
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            APIError: If the deletion fails
        """
        data: ReactionRequest = {
            'reaction': reaction
        }
        
        self._http.request(
            'DELETE',
            f"/comment/{table_id}/{record_id}/{comment_id}/reaction",
            json=data
        )
        return True
