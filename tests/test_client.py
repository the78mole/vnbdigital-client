"""Tests for vnbdigital_client module."""

import pytest
from unittest.mock import Mock, patch
from vnbdigital_client import VNBDigitalClient


class TestVNBDigitalClient:
    """Test cases for VNBDigitalClient."""
    
    def test_client_initialization(self):
        """Test that client can be initialized."""
        client = VNBDigitalClient()
        assert client is not None
        assert client.api_url == VNBDigitalClient.DEFAULT_API_URL
    
    def test_client_with_custom_url(self):
        """Test that client can be initialized with custom URL."""
        custom_url = "https://custom.api/graphql"
        client = VNBDigitalClient(api_url=custom_url)
        assert client.api_url == custom_url
    
    def test_client_with_api_key(self):
        """Test that client can be initialized with API key."""
        api_key = "test-api-key"
        client = VNBDigitalClient(api_key=api_key)
        assert client.api_key == api_key
    
    @patch('vnbdigital_client.client.Client')
    def test_search(self, mock_client_class):
        """Test search functionality."""
        mock_client = Mock()
        mock_client.execute.return_value = {
            "search": [
                {"id": "1", "title": "Test Item", "description": "Test", "url": "http://test.com"}
            ]
        }
        mock_client_class.return_value = mock_client
        
        client = VNBDigitalClient()
        results = client.search("test query", limit=10)
        
        assert len(results) == 1
        assert results[0]["id"] == "1"
        assert results[0]["title"] == "Test Item"
    
    @patch('vnbdigital_client.client.Client')
    def test_get_item(self, mock_client_class):
        """Test get_item functionality."""
        mock_client = Mock()
        mock_client.execute.return_value = {
            "item": {
                "id": "123",
                "title": "Test Item",
                "description": "A test item",
                "url": "http://test.com"
            }
        }
        mock_client_class.return_value = mock_client
        
        client = VNBDigitalClient()
        item = client.get_item("123")
        
        assert item is not None
        assert item["id"] == "123"
        assert item["title"] == "Test Item"
    
    @patch('vnbdigital_client.client.Client')
    def test_list_collections(self, mock_client_class):
        """Test list_collections functionality."""
        mock_client = Mock()
        mock_client.execute.return_value = {
            "collections": [
                {"id": "1", "name": "Collection 1", "description": "Test", "itemCount": 10}
            ]
        }
        mock_client_class.return_value = mock_client
        
        client = VNBDigitalClient()
        collections = client.list_collections()
        
        assert len(collections) == 1
        assert collections[0]["id"] == "1"
        assert collections[0]["name"] == "Collection 1"
    
    @patch('vnbdigital_client.client.Client')
    def test_get_collection(self, mock_client_class):
        """Test get_collection functionality."""
        mock_client = Mock()
        mock_client.execute.return_value = {
            "collection": {
                "id": "1",
                "name": "Test Collection",
                "description": "A test collection",
                "items": [
                    {"id": "1", "title": "Item 1", "description": "Test", "url": "http://test.com"}
                ]
            }
        }
        mock_client_class.return_value = mock_client
        
        client = VNBDigitalClient()
        collection = client.get_collection("1", limit=50)
        
        assert collection is not None
        assert collection["id"] == "1"
        assert collection["name"] == "Test Collection"
        assert len(collection["items"]) == 1
