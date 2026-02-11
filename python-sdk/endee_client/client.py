"""
Main client class for interacting with Endee vector database.
"""

import json
from typing import Optional, List, Dict, Any, Union
import requests
from .exceptions import EndeeConnectionError, EndeeAPIError


class EndeeClient:
    """
    Client for interacting with Endee vector database.
    
    Args:
        base_url: Base URL of the Endee server (e.g., 'http://localhost:8080')
        auth_token: Optional authentication token (required if server has NDD_AUTH_TOKEN set)
        timeout: Request timeout in seconds (default: 30)
    
    Example:
        >>> client = EndeeClient('http://localhost:8080')
        >>> client.health_check()
        {'status': 'ok'}
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        auth_token: Optional[str] = None,
        timeout: int = 30
    ):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.timeout = timeout
        self._session = requests.Session()
        
        if self.auth_token:
            self._session.headers.update({
                'Authorization': self.auth_token
            })
    
    def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Union[Dict[str, Any], List[Any]]:
        """
        Make an HTTP request to the Endee API.
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint path
            json_data: JSON data to send in request body
            params: Query parameters
            headers: Additional headers
            
        Returns:
            Response data as dictionary or list
            
        Raises:
            EndeeConnectionError: If connection fails
            EndeeAPIError: If API returns an error
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self._session.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            
            # Check for errors
            if response.status_code >= 400:
                error_msg = f"API request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg = error_data['error']
                except:
                    error_msg = response.text or error_msg
                
                raise EndeeAPIError(
                    error_msg,
                    status_code=response.status_code,
                    response_body=response.text
                )
            
            # Parse response
            if response.text:
                return response.json()
            return {}
            
        except requests.exceptions.RequestException as e:
            raise EndeeConnectionError(f"Failed to connect to Endee server: {e}")
    
    # Health and Info APIs
    
    def health_check(self) -> Dict[str, str]:
        """
        Check if the Endee server is healthy.
        
        Returns:
            Health status dictionary
        """
        return self._request('GET', '/api/v1/health')
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get server statistics.
        
        Returns:
            Server statistics dictionary
        """
        return self._request('GET', '/api/v1/stats')
    
    # Index Management APIs
    
    def create_index(
        self,
        index_name: str,
        dim: int,
        space_type: str = "l2",
        ef_construction: int = 200,
        m: int = 16,
        quant_type: str = "none",
        enable_sparse: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new vector index.
        
        Args:
            index_name: Name of the index
            dim: Dimensionality of vectors
            space_type: Distance metric ('l2', 'ip', 'cosine')
            ef_construction: HNSW ef_construction parameter (default: 200)
            m: HNSW M parameter (default: 16)
            quant_type: Quantization type ('none', 'scalar', 'product')
            enable_sparse: Enable sparse vector support (default: False)
            
        Returns:
            Response dictionary with index creation status
        """
        data = {
            "index_name": index_name,
            "dim": dim,
            "space_type": space_type,
            "ef_construction": ef_construction,
            "m": m,
            "quant_type": quant_type,
            "enable_sparse": enable_sparse
        }
        return self._request('POST', '/api/v1/index/create', json_data=data)
    
    def list_indexes(self) -> Dict[str, Any]:
        """
        List all indexes.
        
        Returns:
            Dictionary containing list of indexes
        """
        return self._request('GET', '/api/v1/index/list')
    
    def get_index_info(self, index_name: str) -> Dict[str, Any]:
        """
        Get information about a specific index.
        
        Args:
            index_name: Name of the index
            
        Returns:
            Index information dictionary
        """
        return self._request('GET', f'/api/v1/index/{index_name}/info')
    
    def delete_index(self, index_name: str) -> Dict[str, Any]:
        """
        Delete an index.
        
        Args:
            index_name: Name of the index to delete
            
        Returns:
            Deletion status dictionary
        """
        return self._request('DELETE', f'/api/v1/index/{index_name}/delete')
    
    # Vector Operations APIs
    
    def insert_vectors(
        self,
        index_name: str,
        vectors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Insert vectors into an index.
        
        Args:
            index_name: Name of the index
            vectors: List of vector objects. Each object should contain:
                - id: Unique identifier for the vector
                - vector: List of floats representing the vector
                - sparse_vector: (optional) Sparse vector representation
                - metadata: (optional) Dictionary of metadata
                
        Example:
            >>> vectors = [
            ...     {
            ...         "id": "vec1",
            ...         "vector": [0.1, 0.2, 0.3],
            ...         "metadata": {"category": "A"}
            ...     }
            ... ]
            >>> client.insert_vectors("my_index", vectors)
            
        Returns:
            Insertion status dictionary
        """
        return self._request(
            'POST',
            f'/api/v1/index/{index_name}/vector/insert',
            json_data=vectors
        )
    
    def search_vectors(
        self,
        index_name: str,
        vector: List[float],
        k: int = 10,
        ef_search: Optional[int] = None,
        filter_expr: Optional[str] = None,
        sparse_vector: Optional[Dict[int, float]] = None
    ) -> Dict[str, Any]:
        """
        Search for similar vectors in an index.
        
        Args:
            index_name: Name of the index
            vector: Query vector
            k: Number of results to return (default: 10)
            ef_search: HNSW ef_search parameter (optional)
            filter_expr: Filter expression for metadata filtering (optional)
            sparse_vector: Sparse vector for hybrid search (optional)
            
        Returns:
            Search results dictionary containing matched vectors with distances
        """
        data = {
            "vector": vector,
            "k": k
        }
        
        if ef_search is not None:
            data["ef_search"] = ef_search
        if filter_expr:
            data["filter"] = filter_expr
        if sparse_vector:
            data["sparse_vector"] = sparse_vector
            
        return self._request(
            'POST',
            f'/api/v1/index/{index_name}/search',
            json_data=data
        )
    
    def get_vector(self, index_name: str, vector_ids: List[str]) -> Dict[str, Any]:
        """
        Get vectors by their IDs.
        
        Args:
            index_name: Name of the index
            vector_ids: List of vector IDs to retrieve
            
        Returns:
            Dictionary containing the requested vectors
        """
        data = {"ids": vector_ids}
        return self._request(
            'POST',
            f'/api/v1/index/{index_name}/vector/get',
            json_data=data
        )
    
    def delete_vector(self, index_name: str, vector_id: str) -> Dict[str, Any]:
        """
        Delete a single vector by ID.
        
        Args:
            index_name: Name of the index
            vector_id: ID of the vector to delete
            
        Returns:
            Deletion status dictionary
        """
        return self._request(
            'DELETE',
            f'/api/v1/index/{index_name}/vector/{vector_id}/delete'
        )
    
    def delete_vectors(self, index_name: str, vector_ids: List[str]) -> Dict[str, Any]:
        """
        Delete multiple vectors by IDs.
        
        Args:
            index_name: Name of the index
            vector_ids: List of vector IDs to delete
            
        Returns:
            Deletion status dictionary
        """
        data = {"ids": vector_ids}
        return self._request(
            'POST',
            f'/api/v1/index/{index_name}/vectors/delete',
            json_data=data
        )
    
    def update_filters(
        self,
        index_name: str,
        updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Update metadata filters for vectors.
        
        Args:
            index_name: Name of the index
            updates: List of update operations
            
        Returns:
            Update status dictionary
        """
        return self._request(
            'POST',
            f'/api/v1/index/{index_name}/filters/update',
            json_data=updates
        )
    
    # Backup APIs
    
    def create_backup(self, index_name: str) -> Dict[str, Any]:
        """
        Create a backup of an index.
        
        Args:
            index_name: Name of the index to backup
            
        Returns:
            Backup creation status dictionary
        """
        return self._request('POST', f'/api/v1/index/{index_name}/backup')
    
    def list_backups(self) -> Dict[str, Any]:
        """
        List all available backups.
        
        Returns:
            Dictionary containing list of backups
        """
        return self._request('GET', '/api/v1/backups')
    
    def restore_backup(self, backup_name: str) -> Dict[str, Any]:
        """
        Restore an index from a backup.
        
        Args:
            backup_name: Name of the backup to restore
            
        Returns:
            Restore status dictionary
        """
        return self._request('POST', f'/api/v1/backups/{backup_name}/restore')
    
    def delete_backup(self, backup_name: str) -> Dict[str, Any]:
        """
        Delete a backup.
        
        Args:
            backup_name: Name of the backup to delete
            
        Returns:
            Deletion status dictionary
        """
        return self._request('DELETE', f'/api/v1/backups/{backup_name}')
    
    def close(self):
        """Close the session."""
        self._session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
