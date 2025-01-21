"""
Main client module.

This module provides the main TeableClient class that serves as a facade for all managers.
"""

from typing import Any, Dict, Union

from ..models.config import TeableConfig
from ..models.space import Space
from ..models.base import Base
from ..models.table import Table
from ..models.field import Field
from ..models.view import View
from .http import TeableHttpClient
from .cache import ResourceCache
from .auth import AuthManager
from .tables import TableManager
from .records import RecordManager
from .fields import FieldManager
from .views import ViewManager
from .spaces import SpaceManager
from .attachments import AttachmentManager
from .selection import SelectionManager

class TeableClient:
    """
    Main client class for interacting with the Teable API.
    
    This class serves as a facade for all specialized managers:
    - Authentication and user management (auth)
    - Space and base management (spaces)
    - Table management (tables)
    - Record management (records)
    - Field management (fields)
    - View management (views)
    - Attachment management (attachments)
    - Selection management (selection)
    """
    
    def __init__(self, config: Union[TeableConfig, Dict[str, Any]]):
        """
        Initialize the client with configuration.
        
        Args:
            config: Configuration instance or dictionary
        """
        if isinstance(config, dict):
            self.config = TeableConfig.from_dict(config)
        else:
            self.config = config
            
        # Initialize HTTP client
        self._http = TeableHttpClient(self.config)
        
        # Initialize caches
        self._space_cache = ResourceCache[Space]()
        self._base_cache = ResourceCache[Base]()
        self._table_cache = ResourceCache[Table]()
        self._field_cache = ResourceCache[Field]()
        self._view_cache = ResourceCache[View]()
        
        # Initialize managers
        self.auth = AuthManager(self._http)
        self.spaces = SpaceManager(self._http, self._space_cache, self._base_cache)
        self.tables = TableManager(self._http, self._table_cache)
        self.records = RecordManager(self._http)
        self.fields = FieldManager(self._http, self._field_cache)
        self.views = ViewManager(self._http, self._view_cache)
        self.attachments = AttachmentManager(self._http)
        self.selection = SelectionManager(self._http)
        
    def clear_cache(self) -> None:
        """Clear all cached resources."""
        self._space_cache.clear_all()
        self._base_cache.clear_all()
        self._table_cache.clear_all()
        self._field_cache.clear_all()
        self._view_cache.clear_all()
