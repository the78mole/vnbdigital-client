"""
vnbdigital-client: A Python client for accessing vnbdigital.de grid operator data.

This package provides a simple API to look up Verteilnetzbetreiber (grid operators)
via the vnbdigital.de GraphQL gateway.
"""

__version__ = "0.1.0"

from vnbdigital_client.client import Operator, Region, VNBDigitalClient

__all__ = ["Operator", "Region", "VNBDigitalClient"]
