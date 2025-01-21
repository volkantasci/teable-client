"""
Attachment management module.

This module handles attachment operations including uploads, downloads, and metadata management.
"""

from typing import Any, Dict, Optional

from .http import TeableHttpClient

class AttachmentManager:
    """
    Handles attachment operations.
    
    This class manages:
    - Attachment uploads and downloads
    - Attachment metadata
    - Attachment signatures
    - Attachment notifications
    """
    
    def __init__(self, http_client: TeableHttpClient):
        """
        Initialize the attachment manager.
        
        Args:
            http_client: HTTP client for API communication
        """
        self._http = http_client
        
    def upload_attachment(
        self,
        table_id: str,
        record_id: str,
        field_id: str,
        file: Optional[bytes] = None,
        file_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload an attachment for a record field.
        
        Args:
            table_id: ID of the table
            record_id: ID of the record
            field_id: ID of the attachment field
            file: Optional file data to upload
            file_url: Optional URL to file
            
        Returns:
            Dict[str, Any]: Updated record data
            
        Raises:
            APIError: If the upload fails
            ValueError: If neither file nor file_url is provided
        """
        if not file and not file_url:
            raise ValueError("Either file or file_url must be provided")
            
        data = {}
        if file:
            data['file'] = ('file', file, 'application/octet-stream')
        if file_url:
            data['fileUrl'] = (None, file_url)
            
        return self._http.request(
            'POST',
            f"table/{table_id}/record/{record_id}/{field_id}/uploadAttachment",
            files=data
        )
        
    def notify_attachment(
        self,
        token: str,
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get Attachment information.
        
        Args:
            token: Token for the attachment
            filename: Optional filename
            
        Returns:
            Dict[str, Any]: Attachment information containing:
                - token: Token for the uploaded file
                - size: File size in bytes
                - url: URL of the uploaded file
                - path: File path
                - mimetype: MIME type of the file
                - width: Optional image width
                - height: Optional image height
                - presignedUrl: Preview URL
            
        Raises:
            APIError: If the request fails
        """
        params = {}
        if filename:
            params['filename'] = filename
            
        return self._http.request(
            'POST',
            f"attachments/notify/{token}",
            params=params
        )
        
    def get_attachment(
        self,
        token: str,
        filename: Optional[str] = None
    ) -> bytes:
        """
        Download an attachment.
        
        Args:
            token: Token for the attachment
            filename: Optional filename for download
            
        Returns:
            bytes: Attachment data
            
        Raises:
            APIError: If the request fails
        """
        params = {}
        if filename:
            params['filename'] = filename
            
        response = self._http.session.get(
            f"{self._http.config.base_url}/attachments/{token}",
            params=params,
            headers={
                'Authorization': f'Bearer {self._http.config.api_key}'
            },
            stream=True
        )
        response.raise_for_status()
        return response.content
        
    def get_attachment_signature(
        self,
        content_type: str,
        content_length: int,
        attachment_type: int,
        expires_in: Optional[int] = None,
        hash_value: Optional[str] = None,
        base_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve upload signature.
        
        Args:
            content_type: Mime type of the file
            content_length: Size of the file in bytes
            attachment_type: Type of attachment (1-7)
            expires_in: Optional token expiration time in seconds
            hash_value: Optional file hash
            base_id: Optional base ID
            
        Returns:
            Dict[str, Any]: Upload signature containing:
                - url: Upload URL
                - uploadMethod: Upload method (e.g. POST)
                - token: Secret key
                - requestHeaders: Headers for upload request
            
        Raises:
            APIError: If the request fails
            ValueError: If attachment_type is not between 1 and 7
        """
        if not 1 <= attachment_type <= 7:
            raise ValueError("attachment_type must be between 1 and 7")
            
        data: Dict[str, Any] = {
            'contentType': content_type,
            'contentLength': content_length,
            'type': attachment_type
        }
        if expires_in is not None:
            data['expiresIn'] = expires_in
        if hash_value is not None:
            data['hash'] = hash_value
        if base_id is not None:
            data['baseId'] = base_id
            
        return self._http.request(
            'POST',
            "attachments/signature",
            json=data
        )
        
    def upload_attachment_with_token(
        self,
        token: str,
        file_data: bytes
    ) -> bool:
        """
        Upload attachment with token.
        
        Args:
            token: Upload token from get_attachment_signature
            file_data: Binary file data to upload
            
        Returns:
            bool: True if upload successful
            
        Raises:
            APIError: If the upload fails
        """
        self._http.request(
            'POST',
            f"attachments/upload/{token}",
            data=file_data,
            headers={
                'Content-Type': 'application/octet-stream'
            }
        )
        return True
