"""
vnbdigital-client: A Python client for accessing vnbdigital.de database.

This package provides a simple API to interact with the vnbdigital.de database,
abstracting all complex GraphQL operations from the user.
"""

__version__ = "0.1.0"

from vnbdigital_client.client import VNBDigitalClient

__all__ = ["VNBDigitalClient"]
