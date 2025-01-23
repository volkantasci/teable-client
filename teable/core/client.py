"""
Main client module.

This module provides the main TeableClient class that serves as a facade for all managers.
"""

from typing import Any, Dict, TypeVar, Union

from ..models.config import TeableConfig
from ..models.space import Space
from ..models.base import Base
from ..models.table import Table
from ..models.field import Field
from ..models.view import View

T = TypeVar('T', Space, Base, Table, Field, View)
from .http import TeableHttpClient
from .cache import ResourceCache
from .auth import AuthManager
from .organizations import OrganizationManager
from .ai import AIManager
from .integrity import IntegrityManager
from .tables import TableManager
from .records import RecordManager
from .fields import FieldManager
from .views import ViewManager
from .spaces import SpaceManager
from .attachments import AttachmentManager
from .selection import SelectionManager
from .notifications import NotificationManager
from .access_tokens import AccessTokenManager
from .imports import ImportManager
from .exports import ExportManager
from .pins import PinManager
from .billing import BillingManager
from .admin import AdminManager
from .usage import UsageManager
from .oauth import OAuthManager
from .undo_redo import UndoRedoManager
from .plugins import PluginManager
from .comments import CommentManager
from .aggregation import AggregationManager

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
    - Notification management (notifications)
    - Access token management (access_tokens)
    - Import management (imports)
    - Export management (exports)
    - Pin management (pins)
    - Billing management (billing)
    - Admin management (admin)
    - Usage management (usage)
    - OAuth application management (oauth)
    - Undo/redo operations (undo_redo)
    - Plugin management (plugins)
    - Comment management (comments)
    - Organization management (organizations)
    - AI generation (ai)
    - Data integrity checks (integrity)
    - Aggregation operations (aggregation)
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
        
        # Initialize caches with specific types
        self._space_cache = ResourceCache[Space]()  # type: ResourceCache[Space]
        self._base_cache = ResourceCache[Base]()    # type: ResourceCache[Base]
        self._table_cache = ResourceCache[Table]()  # type: ResourceCache[Table]
        self._field_cache = ResourceCache[Field]()  # type: ResourceCache[Field]
        self._view_cache = ResourceCache[View]()    # type: ResourceCache[View]
        
        # Initialize managers
        self.auth = AuthManager(self._http)
        self.spaces = SpaceManager(self._http, self._space_cache, self._base_cache)
        self.tables = TableManager(self._http, self._table_cache)
        self.records = RecordManager(self._http)
        self.fields = FieldManager(self._http, self._field_cache)
        self.views = ViewManager(self._http, self._view_cache)
        self.attachments = AttachmentManager(self._http)
        self.selection = SelectionManager(self._http)
        self.notifications = NotificationManager(self._http)
        self.access_tokens = AccessTokenManager(self._http)
        self.imports = ImportManager(self._http)
        self.exports = ExportManager(self._http)
        self.pins = PinManager(self._http)
        self.billing = BillingManager(self._http)
        self.admin = AdminManager(self._http)
        self.usage = UsageManager(self._http)
        self.oauth = OAuthManager(self._http)
        self.undo_redo = UndoRedoManager(self._http)
        self.plugins = PluginManager(self._http)
        self.comments = CommentManager(self._http)
        self.organizations = OrganizationManager(self._http)
        self.ai = AIManager(self._http)
        self.integrity = IntegrityManager(self._http)
        self.aggregation = AggregationManager(self._http)
        
    def clear_cache(self) -> None:
        """Clear all cached resources."""
        self._space_cache.clear_all()
        self._base_cache.clear_all()
        self._table_cache.clear_all()
        self._field_cache.clear_all()
        self._view_cache.clear_all()
