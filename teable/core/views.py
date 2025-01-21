"""
View management module.

This module handles view operations including creation, modification, and configuration.
"""

from typing import Any, Dict, List, Optional

from ..models.view import View
from ..models.plugin import PluginInstallation
from .http import TeableHttpClient
from .cache import ResourceCache

class ViewManager:
    """
    Handles view operations.
    
    This class manages:
    - View creation and deletion
    - View configuration updates
    - View sharing settings
    - View plugins
    - View caching
    """
    
    def __init__(self, http_client: TeableHttpClient, cache: ResourceCache[View]):
        """
        Initialize the view manager.
        
        Args:
            http_client: HTTP client for API communication
            cache: Resource cache for views
        """
        self._http = http_client
        self._cache = cache
        self._cache.add_resource_type('views')
        
    def get_view(self, table_id: str, view_id: str) -> View:
        """
        Get a view by ID.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            
        Returns:
            View: The requested view
            
        Raises:
            APIError: If the request fails
        """
        cache_key = f"{table_id}_{view_id}"
        cached = self._cache.get('views', cache_key)
        if cached:
            return cached
            
        response = self._http.request(
            'GET',
            f"table/{table_id}/view/{view_id}"
        )
        view = View.from_api_response(response, self)
        self._cache.set('views', cache_key, view)
        return view
        
    def get_table_views(self, table_id: str) -> List[View]:
        """
        Get all views for a table.
        
        Args:
            table_id: ID of the table
            
        Returns:
            List[View]: List of views
            
        Raises:
            APIError: If the request fails
        """
        response = self._http.request('GET', f"table/{table_id}/view")
        views = [View.from_api_response(v, self) for v in response]
        
        # Update cache
        for view in views:
            cache_key = f"{table_id}_{view.view_id}"
            self._cache.set('views', cache_key, view)
            
        return views
        
    def create_view(
        self,
        table_id: str,
        view_type: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        order: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
        sort: Optional[Dict[str, Any]] = None,
        filter: Optional[Dict[str, Any]] = None,
        group: Optional[List[Dict[str, Any]]] = None,
        share_id: Optional[str] = None,
        enable_share: Optional[bool] = None,
        share_meta: Optional[Dict[str, Any]] = None,
        column_meta: Optional[Dict[str, Any]] = None,
        plugin_id: Optional[str] = None
    ) -> View:
        """
        Create a new view in a table.
        
        Args:
            table_id: ID of the table
            view_type: Type of view ('grid', 'calendar', 'kanban', 'form', 'gallery', 'gantt', 'plugin')
            name: Optional display name for the view
            description: Optional description
            order: Optional order position
            options: Optional view-specific options
            sort: Optional sort configuration
            filter: Optional filter configuration
            group: Optional group configuration
            share_id: Optional share ID
            enable_share: Optional enable sharing flag
            share_meta: Optional sharing metadata
            column_meta: Optional column metadata
            plugin_id: Optional plugin ID
            
        Returns:
            View: The created view
            
        Raises:
            APIError: If the creation fails
        """
        data: Dict[str, Any] = {'type': view_type}
        
        if name is not None:
            data['name'] = name
        if description is not None:
            data['description'] = description
        if order is not None:
            data['order'] = order
        if options is not None:
            data['options'] = options
        if sort is not None:
            data['sort'] = sort
        if filter is not None:
            data['filter'] = filter
        if group is not None:
            data['group'] = group
        if share_id is not None:
            data['shareId'] = share_id
        if enable_share is not None:
            data['enableShare'] = enable_share
        if share_meta is not None:
            data['shareMeta'] = share_meta
        if column_meta is not None:
            data['columnMeta'] = column_meta
        if plugin_id is not None:
            data['pluginId'] = plugin_id
            
        response = self._http.request(
            'POST',
            f"table/{table_id}/view",
            json=data
        )
        view = View.from_api_response(response, self)
        cache_key = f"{table_id}_{view.view_id}"
        self._cache.set('views', cache_key, view)
        return view
        
    def delete_view(self, table_id: str, view_id: str) -> bool:
        """
        Delete a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            APIError: If the deletion fails
        """
        self._http.request(
            'DELETE',
            f"table/{table_id}/view/{view_id}"
        )
        cache_key = f"{table_id}_{view_id}"
        self._cache.delete('views', cache_key)
        return True
        
    def update_view_manual_sort(
        self,
        table_id: str,
        view_id: str,
        sort_objects: List[Dict[str, str]]
    ) -> bool:
        """
        Update manual sort configuration for a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            sort_objects: List of sort configurations, each containing:
                - fieldId: ID of the field to sort by
                - order: Sort direction ('asc' or 'desc')
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._http.request(
            'PUT',
            f"table/{table_id}/view/{view_id}/manual-sort",
            json={'sortObjs': sort_objects}
        )
        cache_key = f"{table_id}_{view_id}"
        self._cache.delete('views', cache_key)
        return True
        
    def update_view_column_meta(
        self,
        table_id: str,
        view_id: str,
        column_meta_updates: List[Dict[str, Any]]
    ) -> bool:
        """
        Update column metadata for a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            column_meta_updates: List of column metadata updates, each containing:
                - fieldId: ID of the field
                - columnMeta: Column metadata configuration
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._http.request(
            'PUT',
            f"table/{table_id}/view/{view_id}/column-meta",
            json=column_meta_updates
        )
        cache_key = f"{table_id}_{view_id}"
        self._cache.delete('views', cache_key)
        return True
        
    def update_view_filter(
        self,
        table_id: str,
        view_id: str,
        filter_config: Dict[str, Any]
    ) -> bool:
        """
        Update filter configuration for a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            filter_config: Filter configuration containing:
                - filterSet: List of filter conditions
                - conjunction: How to combine conditions ('and' or 'or')
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._http.request(
            'PUT',
            f"table/{table_id}/view/{view_id}/filter",
            json={'filter': filter_config}
        )
        cache_key = f"{table_id}_{view_id}"
        self._cache.delete('views', cache_key)
        return True
        
    def update_view_sort(
        self,
        table_id: str,
        view_id: str,
        sort_objects: List[Dict[str, str]],
        manual_sort: Optional[bool] = None
    ) -> bool:
        """
        Update sort configuration for a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            sort_objects: List of sort configurations
            manual_sort: Optional flag for manual sorting
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        data: Dict[str, Any] = {'sortObjs': sort_objects}
        if manual_sort is not None:
            data['manualSort'] = manual_sort
            
        self._http.request(
            'PUT',
            f"table/{table_id}/view/{view_id}/sort",
            json=data
        )
        cache_key = f"{table_id}_{view_id}"
        self._cache.delete('views', cache_key)
        return True
        
    def update_view_group(
        self,
        table_id: str,
        view_id: str,
        group_objects: Optional[List[Dict[str, str]]] = None
    ) -> bool:
        """
        Update group configuration for a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            group_objects: Optional list of group configurations
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._http.request(
            'PUT',
            f"table/{table_id}/view/{view_id}/group",
            json=group_objects
        )
        cache_key = f"{table_id}_{view_id}"
        self._cache.delete('views', cache_key)
        return True
        
    def update_view_options(
        self,
        table_id: str,
        view_id: str,
        options: Dict[str, Any]
    ) -> bool:
        """
        Update options for a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            options: View options configuration
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._http.request(
            'PATCH',
            f"table/{table_id}/view/{view_id}/options",
            json={'options': options}
        )
        cache_key = f"{table_id}_{view_id}"
        self._cache.delete('views', cache_key)
        return True
        
    def update_view_name(
        self,
        table_id: str,
        view_id: str,
        name: str
    ) -> bool:
        """
        Update name of a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            name: New name for the view
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._http.request(
            'PUT',
            f"table/{table_id}/view/{view_id}/name",
            json={'name': name}
        )
        cache_key = f"{table_id}_{view_id}"
        self._cache.delete('views', cache_key)
        return True
        
    def update_view_description(
        self,
        table_id: str,
        view_id: str,
        description: str
    ) -> bool:
        """
        Update description of a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            description: New description for the view
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._http.request(
            'PUT',
            f"table/{table_id}/view/{view_id}/description",
            json={'description': description}
        )
        cache_key = f"{table_id}_{view_id}"
        self._cache.delete('views', cache_key)
        return True
        
    def update_view_share_meta(
        self,
        table_id: str,
        view_id: str,
        allow_copy: Optional[bool] = None,
        include_hidden_field: Optional[bool] = None,
        password: Optional[str] = None,
        include_records: Optional[bool] = None,
        submit_allow: Optional[bool] = None,
        submit_require_login: Optional[bool] = None
    ) -> bool:
        """
        Update share metadata for a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            allow_copy: Whether to allow copying of shared data
            include_hidden_field: Whether to include hidden fields
            password: Password protection (min length 3)
            include_records: Whether to include records
            submit_allow: Whether to allow form submissions
            submit_require_login: Whether to require login for submissions
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
            ValueError: If password is too short
        """
        if password is not None and len(password) < 3:
            raise ValueError("Password must be at least 3 characters long")
            
        data: Dict[str, Any] = {}
        if allow_copy is not None:
            data['allowCopy'] = allow_copy
        if include_hidden_field is not None:
            data['includeHiddenField'] = include_hidden_field
        if password is not None:
            data['password'] = password
        if include_records is not None:
            data['includeRecords'] = include_records
        if submit_allow is not None or submit_require_login is not None:
            data['submit'] = {}
            if submit_allow is not None:
                data['submit']['allow'] = submit_allow
            if submit_require_login is not None:
                data['submit']['requireLogin'] = submit_require_login
            
        self._http.request(
            'PUT',
            f"table/{table_id}/view/{view_id}/share-meta",
            json=data
        )
        cache_key = f"{table_id}_{view_id}"
        self._cache.delete('views', cache_key)
        return True
        
    def refresh_view_share_id(
        self,
        table_id: str,
        view_id: str
    ) -> str:
        """
        Refresh share ID for a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            
        Returns:
            str: New share ID
            
        Raises:
            APIError: If the refresh fails
        """
        response = self._http.request(
            'POST',
            f"table/{table_id}/view/{view_id}/refresh-share-id"
        )
        cache_key = f"{table_id}_{view_id}"
        self._cache.delete('views', cache_key)
        return response['shareId']
        
    def disable_view_share(
        self,
        table_id: str,
        view_id: str
    ) -> bool:
        """
        Disable sharing for a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            
        Returns:
            bool: True if sharing was successfully disabled
            
        Raises:
            APIError: If the operation fails
        """
        self._http.request(
            'POST',
            f"table/{table_id}/view/{view_id}/disable-share"
        )
        cache_key = f"{table_id}_{view_id}"
        self._cache.delete('views', cache_key)
        return True
        
    def enable_view_share(
        self,
        table_id: str,
        view_id: str
    ) -> str:
        """
        Enable sharing for a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            
        Returns:
            str: Share ID for the enabled view
            
        Raises:
            APIError: If the operation fails
        """
        response = self._http.request(
            'POST',
            f"table/{table_id}/view/{view_id}/enable-share"
        )
        cache_key = f"{table_id}_{view_id}"
        self._cache.delete('views', cache_key)
        return response['shareId']
        
    def install_view_plugin(
        self,
        table_id: str,
        plugin_id: str,
        name: Optional[str] = None
    ) -> PluginInstallation:
        """
        Install a plugin to create a new plugin view.
        
        Args:
            table_id: ID of the table
            plugin_id: ID of the plugin to install
            name: Optional display name for the plugin view
            
        Returns:
            PluginInstallation: Information about the installed plugin
            
        Raises:
            APIError: If the installation fails
        """
        data: Dict[str, Any] = {'pluginId': plugin_id}
        if name is not None:
            data['name'] = name
            
        response = self._http.request(
            'POST',
            f"table/{table_id}/view/plugin",
            json=data
        )
        return PluginInstallation.from_api_response(response)
