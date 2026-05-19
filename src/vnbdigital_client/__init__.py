"""
vnbdigital-client: A Python client for accessing vnbdigital.de grid operator data.

This package provides a simple API to look up Verteilnetzbetreiber (grid operators)
via the vnbdigital.de GraphQL gateway.
"""

__version__ = "0.1.0"

from vnbdigital_client.client import (
    Operator,
    Postcode,
    Region,
    SearchResult,
    VNBDigitalClient,
    lookup_bdew_by_company_code,
    lookup_bdew_by_market_code,
    lookup_bdew_market_function_detail,
)

__all__ = [
    "Operator",
    "Postcode",
    "Region",
    "SearchResult",
    "VNBDigitalClient",
    "lookup_bdew_by_company_code",
    "lookup_bdew_by_market_code",
    "lookup_bdew_market_function_detail",
]
