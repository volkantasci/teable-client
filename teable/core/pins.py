"""
Pin management module.

This module handles operations for managing pinned spaces and bases.
"""

from typing import Dict, List, Literal, TypedDict

from .http import TeableHttpClient

class Pin(TypedDict):
    """Type definition for a pin."""
    id: str
    type: Literal['space', 'base']
    order: int

class PinOrderUpdate(TypedDict):
    """Type definition for pin order update request."""
    id: str
    type: Literal['space', 'base']
    anchorId: str
    anchorType: Literal['space', 'base']
    position: Literal['before', 'after']

class PinCreate(TypedDict):
    """Type definition for pin creation request."""
    type: Literal['space', 'base']
    id: str

class PinManager:
    """
    Handles pin operations.
    
    This class manages:
    - Pin creation and deletion
    - Pin listing and ordering
    - Pin management for spaces and bases
    """
    
    def __init__(self, http_client: TeableHttpClient):
        """
        Initialize the pin manager.
        
        Args:
            http_client: HTTP client for API communication
        """
        self._http = http_client
        
    def create_pin(
        self,
        pin_type: Literal['space', 'base'],
        pin_id: str
    ) -> bool:
        """
        Add a pin to a space or base.
        
        Args:
            pin_type: Type of pin ('space' or 'base')
            pin_id: ID of the space or base to pin
            
        Returns:
            bool: True if creation successful
            
        Raises:
            APIError: If the creation fails
            ValueError: If pin_type is invalid
        """
        if pin_type not in ('space', 'base'):
            raise ValueError("pin_type must be either 'space' or 'base'")
            
        data: PinCreate = {
            'type': pin_type,
            'id': pin_id
        }
        
        self._http.request(
            'POST',
            '/pin/',
            json=data
        )
        return True
        
    def update_pin_order(
        self,
        pin_id: str,
        pin_type: Literal['space', 'base'],
        anchor_id: str,
        anchor_type: Literal['space', 'base'],
        position: Literal['before', 'after']
    ) -> bool:
        """
        Update the order of a pin relative to another pin.
        
        Args:
            pin_id: ID of the pin to move
            pin_type: Type of pin to move ('space' or 'base')
            anchor_id: ID of the reference pin
            anchor_type: Type of reference pin ('space' or 'base')
            position: Where to place the pin ('before' or 'after' the anchor)
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
            ValueError: If pin_type, anchor_type, or position is invalid
        """
        if pin_type not in ('space', 'base'):
            raise ValueError("pin_type must be either 'space' or 'base'")
        if anchor_type not in ('space', 'base'):
            raise ValueError("anchor_type must be either 'space' or 'base'")
        if position not in ('before', 'after'):
            raise ValueError("position must be either 'before' or 'after'")
            
        data: PinOrderUpdate = {
            'id': pin_id,
            'type': pin_type,
            'anchorId': anchor_id,
            'anchorType': anchor_type,
            'position': position
        }
        
        self._http.request(
            'PUT',
            '/pin/order',
            json=data
        )
        return True
        
    def list_pins(self) -> List[Pin]:
        """
        Get list of all pins.
        
        Returns:
            List[Pin]: List of pins, each containing:
                - id: ID of the pinned space or base
                - type: Type of pin ('space' or 'base')
                - order: Display order of the pin
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(
            'GET',
            '/pin/list'
        )
        
    def delete_pin(
        self,
        pin_type: Literal['space', 'base'],
        pin_id: str
    ) -> bool:
        """
        Delete a pin from a space or base.
        
        Args:
            pin_type: Type of pin ('space' or 'base')
            pin_id: ID of the space or base to unpin
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            APIError: If the deletion fails
            ValueError: If pin_type is invalid
        """
        if pin_type not in ('space', 'base'):
            raise ValueError("pin_type must be either 'space' or 'base'")
            
        self._http.request(
            'DELETE',
            '/pin',
            params={
                'type': pin_type,
                'id': pin_id
            }
        )
        return True
