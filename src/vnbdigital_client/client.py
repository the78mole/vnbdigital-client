"""
Main client for vnbdigital.de API.

This module provides the VNBDigitalClient class which abstracts GraphQL operations
to provide a simple Python API for accessing vnbdigital.de data.
"""

from typing import Any, Dict, List, Optional
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport


class VNBDigitalClient:
    """
    Client for accessing vnbdigital.de database.

    This client abstracts the GraphQL API and provides simple methods
    to query and retrieve data from vnbdigital.de.

    Args:
        api_url: The GraphQL API endpoint URL (default: vnbdigital.de API)
        api_key: Optional API key for authentication
    """

    DEFAULT_API_URL = "https://vnbdigital.de/api/graphql"

    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None) -> None:
        """Initialize the vnbdigital client."""
        self.api_url = api_url or self.DEFAULT_API_URL
        self.api_key = api_key

        # Setup transport with optional authentication
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        transport = RequestsHTTPTransport(
            url=self.api_url,
            headers=headers,
            verify=True,
            retries=3,
        )

        self.client = Client(transport=transport, fetch_schema_from_transport=False)

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for items in the vnbdigital database.

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List of search results
        """
        graphql_query = gql("""
            query Search($query: String!, $limit: Int!) {
                search(query: $query, limit: $limit) {
                    id
                    title
                    description
                    url
                }
            }
        """)

        params = {"query": query, "limit": limit}

        try:
            result = self.client.execute(graphql_query, variable_values=params)
            return result.get("search", [])
        except Exception as e:
            raise Exception(f"Search failed: {str(e)}")

    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific item by ID.

        Args:
            item_id: The ID of the item to retrieve

        Returns:
            Item data or None if not found
        """
        graphql_query = gql("""
            query GetItem($id: ID!) {
                item(id: $id) {
                    id
                    title
                    description
                    url
                    metadata
                    createdAt
                    updatedAt
                }
            }
        """)

        params = {"id": item_id}

        try:
            result = self.client.execute(graphql_query, variable_values=params)
            return result.get("item")
        except Exception as e:
            raise Exception(f"Failed to get item: {str(e)}")

    def list_collections(self) -> List[Dict[str, Any]]:
        """
        List all available collections.

        Returns:
            List of collections
        """
        graphql_query = gql("""
            query ListCollections {
                collections {
                    id
                    name
                    description
                    itemCount
                }
            }
        """)

        try:
            result = self.client.execute(graphql_query)
            return result.get("collections", [])
        except Exception as e:
            raise Exception(f"Failed to list collections: {str(e)}")

    def get_collection(self, collection_id: str, limit: int = 50) -> Dict[str, Any]:
        """
        Get items from a specific collection.

        Args:
            collection_id: The ID of the collection
            limit: Maximum number of items to return

        Returns:
            Collection data with items
        """
        graphql_query = gql("""
            query GetCollection($id: ID!, $limit: Int!) {
                collection(id: $id) {
                    id
                    name
                    description
                    items(limit: $limit) {
                        id
                        title
                        description
                        url
                    }
                }
            }
        """)

        params = {"id": collection_id, "limit": limit}

        try:
            result = self.client.execute(graphql_query, variable_values=params)
            return result.get("collection", {})
        except Exception as e:
            raise Exception(f"Failed to get collection: {str(e)}")
