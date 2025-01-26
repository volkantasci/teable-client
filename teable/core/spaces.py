"""
Space and base management module.

This module handles space and base operations including creation, modification, and deletion.
"""

from typing import Any, Dict, List, Literal, Optional, TypedDict, Union

from ..models.space import Space, SpaceRole
from ..models.base import Base
from ..models.trash import ResourceType, TrashResponse
from .http import TeableHttpClient
from .cache import ResourceCache

class SpaceInvitation(TypedDict):
    """Type definition for space invitation response."""
    invitationId: str
    role: SpaceRole
    inviteUrl: str
    invitationCode: str
    createdBy: str
    createdTime: str

class SpaceInvitationUpdate(TypedDict):
    """Type definition for space invitation update response."""
    invitationId: str
    role: SpaceRole

class SpaceInvitationEmailResponse(TypedDict):
    """Type definition for space invitation email response."""
    invitationId: str

class SpaceCollaboratorBase(TypedDict):
    """Base type for space collaborator."""
    role: SpaceRole
    createdTime: str
    type: Literal['user', 'department']
    resourceType: Literal['space', 'base']
    base: Optional[Dict[str, str]]

class SpaceUserCollaborator(SpaceCollaboratorBase):
    """Type definition for user collaborator."""
    userId: str
    userName: str
    email: str
    avatar: Optional[str]
    type: Literal['user']
    isSystem: bool

class SpaceDepartmentCollaborator(SpaceCollaboratorBase):
    """Type definition for department collaborator."""
    departmentId: str
    departmentName: str
    type: Literal['department']

SpaceCollaborator = Union[SpaceUserCollaborator, SpaceDepartmentCollaborator]

class SpaceCollaboratorListResponse(TypedDict):
    """Type definition for collaborator list response."""
    collaborators: List[SpaceCollaborator]
    total: int

class SpaceCollaboratorUpdate(TypedDict):
    """Type definition for collaborator update request."""
    principalId: str
    principalType: Literal['user', 'department']
    role: SpaceRole

class SpaceManager:
    """
    Handles space and base operations.
    
    This class manages:
    - Space creation and deletion
    - Space metadata updates
    - Base creation and deletion
    - Base metadata updates
    - Space/Base caching
    """
    
    def __init__(
        self,
        http_client: TeableHttpClient,
        space_cache: ResourceCache[Space],
        base_cache: ResourceCache[Base]
    ):
        """
        Initialize the space manager.
        
        Args:
            http_client: HTTP client for API communication
            space_cache: Resource cache for spaces
            base_cache: Resource cache for bases
        """
        self._http = http_client
        self._space_cache = space_cache
        self._base_cache = base_cache
        self._space_cache.add_resource_type('spaces')
        self._base_cache.add_resource_type('bases')

    def _make_request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional arguments for the request
            
        Returns:
            Any: Response data
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(method, endpoint, **kwargs)
        
    def get_spaces(self) -> List[Space]:
        """
        Get all accessible spaces.
        
        Returns:
            List[Space]: List of spaces
            
        Raises:
            APIError: If the request fails
        """
        response = self._http.request('GET', "/space")
        spaces = [Space.from_api_response(s, self) for s in response]
        
        # Update cache
        for space in spaces:
            self._space_cache.set('spaces', space.space_id, space)
            
        return spaces
        
    def get_space(self, space_id: str) -> Space:
        """
        Get a space by ID.
        
        Args:
            space_id: ID of the space to retrieve
            
        Returns:
            Space: The requested space
            
        Raises:
            ResourceNotFoundError: If space not found
        """
        cached = self._space_cache.get('spaces', space_id)
        if cached:
            return cached
            
        response = self._http.request('GET', f"/space/{space_id}")
        space = Space.from_api_response(response, self)
        self._space_cache.set('spaces', space_id, space)
        return space
        
    def create_space(self, name: str) -> Space:
        """
        Create a new space.
        
        Args:
            name: Display name for the space
            
        Returns:
            Space: The created space
            
        Raises:
            APIError: If the creation fails
        """
        response = self._http.request(
            'POST',
            "/space",
            json={'name': name}
        )
        space = Space.from_api_response(response, self)
        self._space_cache.set('spaces', space.space_id, space)
        return space
        
    def get_bases(self) -> List[Base]:
        """
        Get all accessible bases.
        
        Returns:
            List[Base]: List of bases
            
        Raises:
            APIError: If the request fails
        """
        response = self._http.request('GET', "/base/access/all")
        bases = [Base.from_api_response(b, self) for b in response]
        
        # Update cache
        for base in bases:
            self._base_cache.set('bases', base.base_id, base)
            
        return bases
        
    def get_shared_bases(self) -> List[Base]:
        """
        Get all shared bases.
        
        Returns:
            List[Base]: List of shared bases
            
        Raises:
            APIError: If the request fails
        """
        response = self._http.request('GET', "/base/shared-base")
        bases = [Base.from_api_response(b, self) for b in response]
        
        # Update cache
        for base in bases:
            self._base_cache.set('bases', base.base_id, base)
            
        return bases
        
    def get_base(self, base_id: str) -> Base:
        """
        Get a base by ID.
        
        Args:
            base_id: ID of the base to retrieve
            
        Returns:
            Base: The requested base
            
        Raises:
            ResourceNotFoundError: If base not found
        """
        cached = self._base_cache.get('bases', base_id)
        if cached:
            return cached
            
        response = self._http.request('GET', f"/base/{base_id}")
        base = Base.from_api_response(response, self)
        self._base_cache.set('bases', base_id, base)
        return base
        
    def create_base(
        self,
        space_id: str,
        name: Optional[str] = None,
        icon: Optional[str] = None
    ) -> Base:
        """
        Create a new base in a space.
        
        Args:
            space_id: ID of the space to create the base in
            name: Optional display name for the base
            icon: Optional icon for the base
            
        Returns:
            Base: The created base
            
        Raises:
            APIError: If the creation fails
        """
        data: Dict[str, Any] = {'spaceId': space_id}
        if name:
            data['name'] = name
        if icon:
            data['icon'] = icon
            
        print("Creating base with data:", data)
        response = self._http.request(
            'POST',
            "/base",
            json=data
        )
        print("API response:", response)
        base = Base.from_api_response(response, self)
        self._base_cache.set('bases', base.base_id, base)
        return base
        
    def duplicate_base(
        self,
        from_base_id: str,
        space_id: str,
        name: Optional[str] = None,
        with_records: bool = False
    ) -> Base:
        """
        Duplicate an existing base.
        
        Args:
            from_base_id: ID of the base to duplicate
            space_id: ID of the space to create the duplicate in
            name: Optional name for the duplicated base
            with_records: Whether to include records in the duplicate
            
        Returns:
            Base: The duplicated base
            
        Raises:
            APIError: If the duplication fails
        """
        data: Dict[str, Any] = {
            'fromBaseId': from_base_id,
            'spaceId': space_id,
            'withRecords': with_records
        }
        if name:
            data['name'] = name
            
        response = self._http.request(
            'POST',
            "/base/duplicate",
            json=data
        )
        base = Base.from_api_response(response, self)
        self._base_cache.set('bases', base.base_id, base)
        return base
        
    def create_base_from_template(
        self,
        space_id: str,
        template_id: str,
        with_records: bool = False
    ) -> Base:
        """
        Create a new base from a template.
        
        Args:
            space_id: ID of the space to create the base in
            template_id: ID of the template to use
            with_records: Whether to include template records
            
        Returns:
            Base: The created base
            
        Raises:
            APIError: If the creation fails
        """
        response = self._http.request(
            'POST',
            "/base/create-from-template",
            json={
                'spaceId': space_id,
                'templateId': template_id,
                'withRecords': with_records
            }
        )
        base = Base.from_api_response(response, self)
        self._base_cache.set('bases', base.base_id, base)
        return base
        
    def get_trash_items(self, resource_type: ResourceType) -> TrashResponse:
        """
        Get items in trash for a specific resource type.
        
        Args:
            resource_type: Type of resources to list ('space' or 'base')
            
        Returns:
            TrashResponse: Trash listing response
            
        Raises:
            APIError: If the request fails
        """
        response = self._http.request(
            'GET',
            '/trash',
            params={'resourceType': resource_type.value}
        )
        return TrashResponse.from_api_response(response)
        
    def get_trash_items_for_resource(
        self,
        resource_id: str,
        resource_type: ResourceType,
        cursor: Optional[str] = None
    ) -> TrashResponse:
        """
        Get trash items for a specific base or table.
        
        Args:
            resource_id: ID of the base or table
            resource_type: Type of resource ('base' or 'table')
            cursor: Optional cursor for pagination
            
        Returns:
            TrashResponse: Trash listing response
            
        Raises:
            APIError: If the request fails
        """
        params: Dict[str, Any] = {
            'resourceId': resource_id,
            'resourceType': resource_type.value
        }
        if cursor:
            params['cursor'] = cursor
            
        response = self._http.request(
            'GET',
            '/trash/items',
            params=params
        )
        return TrashResponse.from_api_response(response)
        
    def reset_trash_items_for_resource(
        self,
        resource_id: str,
        resource_type: ResourceType,
        cursor: Optional[str] = None
    ) -> bool:
        """
        Reset (permanently delete) trash items for a specific base or table.
        
        Args:
            resource_id: ID of the base or table
            resource_type: Type of resource ('base' or 'table')
            cursor: Optional cursor for pagination
            
        Returns:
            bool: True if reset successful
            
        Raises:
            APIError: If the reset fails
        """
        params: Dict[str, Any] = {
            'resourceId': resource_id,
            'resourceType': resource_type.value
        }
        if cursor:
            params['cursor'] = cursor
            
        self._http.request(
            'DELETE',
            '/trash/reset-items',
            params=params
        )
        return True
        
    def list_invitations(self, space_id: str) -> List[SpaceInvitation]:
        """
        List invitation links for a space.
        
        Args:
            space_id: ID of the space
            
        Returns:
            List[SpaceInvitation]: List of invitation information
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(
            'GET',
            f"/space/{space_id}/invitation/link"
        )
        
    def create_invitation(
        self,
        space_id: str,
        role: SpaceRole
    ) -> SpaceInvitation:
        """
        Create an invitation link for a space.
        
        Args:
            space_id: ID of the space
            role: Role to assign to invitees
            
        Returns:
            SpaceInvitation: Created invitation information
            
        Raises:
            APIError: If the creation fails
        """
        return self._http.request(
            'POST',
            f"/space/{space_id}/invitation/link",
            json={'role': role}
        )
        
    def delete_invitation(
        self,
        space_id: str,
        invitation_id: str
    ) -> bool:
        """
        Delete an invitation link.
        
        Args:
            space_id: ID of the space
            invitation_id: ID of the invitation
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            APIError: If the deletion fails
        """
        self._http.request(
            'DELETE',
            f"/space/{space_id}/invitation/link/{invitation_id}"
        )
        return True
        
    def update_invitation(
        self,
        space_id: str,
        invitation_id: str,
        role: SpaceRole
    ) -> SpaceInvitationUpdate:
        """
        Update an invitation link.
        
        Args:
            space_id: ID of the space
            invitation_id: ID of the invitation
            role: New role to assign
            
        Returns:
            SpaceInvitationUpdate: Updated invitation information
            
        Raises:
            APIError: If the update fails
        """
        return self._http.request(
            'PATCH',
            f"/space/{space_id}/invitation/link/{invitation_id}",
            json={'role': role}
        )
        
    def send_invitation_emails(
        self,
        space_id: str,
        emails: List[str],
        role: SpaceRole
    ) -> Dict[str, SpaceInvitationEmailResponse]:
        """
        Send invitation emails.
        
        Args:
            space_id: ID of the space
            emails: List of email addresses
            role: Role to assign to invitees
            
        Returns:
            Dict[str, SpaceInvitationEmailResponse]: Map of email to invitation info
            
        Raises:
            APIError: If sending fails
        """
        return self._http.request(
            'POST',
            f"/space/{space_id}/invitation/email",
            json={
                'emails': emails,
                'role': role
            }
        )
        
    def list_collaborators(
        self,
        space_id: str,
        *,
        include_system: Optional[bool] = None,
        include_base: Optional[bool] = None,
        skip: Optional[int] = None,
        take: Optional[int] = None,
        search: Optional[str] = None,
        type: Optional[Literal['user', 'department']] = None
    ) -> SpaceCollaboratorListResponse:
        """
        List collaborators for a space.
        
        Args:
            space_id: ID of the space
            include_system: Optional flag to include system collaborators
            include_base: Optional flag to include base info
            skip: Optional number of items to skip
            take: Optional number of items to take
            search: Optional search term
            type: Optional filter by collaborator type
            
        Returns:
            SpaceCollaboratorListResponse: List of collaborators and total count
            
        Raises:
            APIError: If the request fails
        """
        params: Dict[str, Any] = {}
        if include_system is not None:
            params['includeSystem'] = include_system
        if include_base is not None:
            params['includeBase'] = include_base
        if skip is not None:
            params['skip'] = skip
        if take is not None:
            params['take'] = take
        if search is not None:
            params['search'] = search
        if type is not None:
            params['type'] = type
            
        return self._http.request(
            'GET',
            f"/space/{space_id}/collaborators",
            params=params
        )
        
    def delete_collaborator(
        self,
        space_id: str,
        principal_id: str,
        principal_type: Literal['user', 'department']
    ) -> bool:
        """
        Delete a collaborator from a space.
        
        Args:
            space_id: ID of the space
            principal_id: ID of the user/department
            principal_type: Type of principal ('user' or 'department')
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            APIError: If the deletion fails
        """
        self._http.request(
            'DELETE',
            f"/space/{space_id}/collaborators",
            params={
                'principalId': principal_id,
                'principalType': principal_type
            }
        )
        return True
        
    def update_collaborator(
        self,
        space_id: str,
        principal_id: str,
        principal_type: Literal['user', 'department'],
        role: SpaceRole
    ) -> bool:
        """
        Update a collaborator's role.
        
        Args:
            space_id: ID of the space
            principal_id: ID of the user/department
            principal_type: Type of principal ('user' or 'department')
            role: New role to assign
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._http.request(
            'PATCH',
            f"/space/{space_id}/collaborators",
            json={
                'principalId': principal_id,
                'principalType': principal_type,
                'role': role
            }
        )
        return True
        
    def restore_trash_item(self, trash_id: str) -> bool:
        """
        Restore an item from trash.
        
        Args:
            trash_id: ID of the trash item to restore
            
        Returns:
            bool: True if restoration successful
            
        Raises:
            APIError: If the restoration fails
        """
        self._http.request(
            'POST',
            f"/trash/restore/{trash_id}"
        )
        return True
        
    def create_db_connection(self, base_id: str) -> Dict[str, Any]:
        """
        Create a database connection URL.
        
        Args:
            base_id: ID of the base
            
        Returns:
            Dict[str, Any]: Connection information containing:
                - dsn: Database connection details
                - connection: Connection pool stats
                - url: Connection URL
            
        Raises:
            APIError: If the creation fails
        """
        return self._http.request(
            'POST',
            f"/base/{base_id}/connection",
            json={'baseId': base_id}
        )
        
    def delete_db_connection(self, base_id: str) -> bool:
        """
        Delete a database connection.
        
        Args:
            base_id: ID of the base
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            APIError: If the deletion fails
        """
        self._http.request(
            'DELETE',
            f"/base/{base_id}/connection"
        )
        return True
        
    def get_db_connection(self, base_id: str) -> Dict[str, Any]:
        """
        Get database connection information.
        
        Args:
            base_id: ID of the base
            
        Returns:
            Dict[str, Any]: Connection information containing:
                - dsn: Database connection details
                - connection: Connection pool stats
                - url: Connection URL
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(
            'GET',
            f"/base/{base_id}/connection"
        )

    def update_base_order(
        self,
        base_id: str,
        anchor_id: str,
        position: Literal['before', 'after']
    ) -> bool:
        """
        Update base order relative to another base.
        
        Args:
            base_id: ID of the base to move
            anchor_id: ID of the base to anchor to
            position: Position relative to anchor ('before' or 'after')
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._http.request(
            'PUT',
            f"/base/{base_id}/order",
            json={
                'anchorId': anchor_id,
                'position': position
            }
        )
        self._base_cache.delete('bases', base_id)
        return True
        
    def get_base_permission(self, base_id: str) -> Dict[str, bool]:
        """
        Get permissions for a base.
        
        Args:
            base_id: ID of the base
            
        Returns:
            Dict[str, bool]: Map of permission names to boolean values
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(
            'GET',
            f"/base/{base_id}/permission"
        )
        
    def query_base(
        self,
        base_id: str,
        query: str,
        cell_format: Literal['json', 'text'] = 'text'
    ) -> List[Dict[str, Any]]:
        """
        Execute a query on a base.
        
        Args:
            base_id: ID of the base
            query: SQL query to execute
            cell_format: Format for cell values ('json' or 'text')
            
        Returns:
            List[Dict[str, Any]]: Query results as a list of records
            
        Raises:
            APIError: If the query fails
        """
        return self._http.request(
            'GET',
            f"/base/{base_id}/query",
            params={
                'query': query,
                'cellFormat': cell_format
            }
        )

    def send_base_invitation_emails(
        self,
        base_id: str,
        emails: List[str],
        role: Literal['creator', 'editor', 'commenter', 'viewer']
    ) -> Dict[str, Dict[str, str]]:
        """
        Send invitation emails for a base.
        
        Args:
            base_id: ID of the base
            emails: List of email addresses
            role: Role to assign to invitees
            
        Returns:
            Dict[str, Dict[str, str]]: Map of email to invitation info
            
        Raises:
            APIError: If sending fails
        """
        return self._http.request(
            'POST',
            f"/base/{base_id}/invitation/email",
            json={
                'emails': emails,
                'role': role
            }
        )
        
    def get_space_bases(self, space_id: str) -> List[Base]:
        """
        Get all bases in a space.
        
        Args:
            space_id: ID of the space
            
        Returns:
            List[Base]: List of bases in the space
            
        Raises:
            APIError: If the request fails
        """
        response = self._http.request('GET', f"/space/{space_id}/base")
        bases = [Base.from_api_response(b, self) for b in response]
        
        # Update cache
        for base in bases:
            self._base_cache.set('bases', base.base_id, base)
            
        return bases
        
    def permanently_delete_base(self, base_id: str) -> bool:
        """
        Permanently delete a base.
        
        Args:
            base_id: ID of the base
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            APIError: If the deletion fails
        """
        self._http.request(
            'DELETE',
            f"/base/{base_id}/permanent"
        )
        self._base_cache.delete('bases', base_id)
        return True
        
    def permanently_delete_space(self, space_id: str) -> bool:
        """
        Permanently delete a space.
        
        Args:
            space_id: ID of the space
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            APIError: If the deletion fails
        """
        self._http.request(
            'DELETE',
            f"/space/{space_id}/permanent"
        )
        self._space_cache.delete('spaces', space_id)
        return True
        
    def add_space_collaborators(
        self,
        space_id: str,
        collaborators: List[Dict[str, str]],
        role: SpaceRole
    ) -> bool:
        """
        Add collaborators to a space.
        
        Args:
            space_id: ID of the space
            collaborators: List of collaborator info, each containing:
                - principalId: ID of the user/department
                - principalType: Type of principal ('user' or 'department')
            role: Role to assign to collaborators
            
        Returns:
            bool: True if addition successful
            
        Raises:
            APIError: If the addition fails
        """
        self._http.request(
            'POST',
            f"/space/{space_id}/collaborator",
            json={
                'collaborators': collaborators,
                'role': role
            }
        )
        return True
        
    def add_base_collaborators(
        self,
        base_id: str,
        collaborators: List[Dict[str, str]],
        role: Literal['creator', 'editor', 'commenter', 'viewer']
    ) -> bool:
        """
        Add collaborators to a base.
        
        Args:
            base_id: ID of the base
            collaborators: List of collaborator info, each containing:
                - principalId: ID of the user/department
                - principalType: Type of principal ('user' or 'department')
            role: Role to assign to collaborators
            
        Returns:
            bool: True if addition successful
            
        Raises:
            APIError: If the addition fails
        """
        self._http.request(
            'POST',
            f"/base/{base_id}/collaborator",
            json={
                'collaborators': collaborators,
                'role': role
            }
        )
        return True
