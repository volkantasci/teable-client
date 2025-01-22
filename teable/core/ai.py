"""
AI management module.

This module handles operations for AI generation.
"""

from typing import Literal, Optional, TypedDict

from .http import TeableHttpClient

AITask = Literal['coding', 'embedding', 'translation']

class AIGenerateRequest(TypedDict, total=False):
    """Type definition for AI generate request."""
    prompt: str
    baseId: str
    task: Optional[AITask]

class AIGenerateResponse(TypedDict):
    """Type definition for AI generate response."""
    result: str

class AIManager:
    """
    Handles AI operations.
    
    This class manages:
    - AI generation
    """
    
    def __init__(self, http_client: TeableHttpClient):
        """
        Initialize the AI manager.
        
        Args:
            http_client: HTTP client for API communication
        """
        self._http = http_client
        
    def generate(
        self,
        prompt: str,
        base_id: str,
        *,
        task: Optional[AITask] = None
    ) -> AIGenerateResponse:
        """
        Generate AI response.
        
        Args:
            prompt: Input prompt for generation
            base_id: ID of the base
            task: Optional task type ('coding', 'embedding', or 'translation')
            
        Returns:
            AIGenerateResponse: Generated result
            
        Raises:
            APIError: If the generation fails
        """
        data: AIGenerateRequest = {
            'prompt': prompt,
            'baseId': base_id
        }
        
        if task is not None:
            data['task'] = task
            
        return self._http.request(
            'POST',
            '/api/ai/generate-stream',
            json=data
        )
