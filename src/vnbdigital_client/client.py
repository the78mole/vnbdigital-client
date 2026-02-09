"""
Main client for vnbdigital.de API.

This module provides the VNBDigitalClient class which abstracts GraphQL operations
to provide a simple Python API for accessing vnbdigital.de grid operator data.

The vnbdigital.de API uses GraphQL with the query ``vnb_vnb(id: $id)`` to look up
grid operators (Verteilnetzbetreiber) by their BDEW code.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import requests


@dataclass
class Region:
    """A geographical region associated with a grid operator."""

    id: str
    name: str


@dataclass
class Operator:
    """Information about a grid operator (Verteilnetzbetreiber).

    Attributes:
        id: Internal vnbdigital ID (``_id``).
        name: Name of the operator.
        address: Street address.
        postcode: Postal code.
        city: City name.
        phone: Phone number.
        contact: Contact information.
        website: Website URL.
        description: Optional description text.
        types: Operator type tags (e.g. ``["Strom"]``).
        layer_url: WMS layer URL for the service-area map.
        bbox: Bounding box coordinates ``[west, south, east, north]``.
        regions: List of :class:`Region` objects.
        image_url: URL of a header image.
        logo_url: URL of the operator's logo.
        public_required: Whether public access is required.
        clicks: Number of clicks/views on vnbdigital.de.
        raw: The full raw API response dict.
    """

    id: str
    name: str
    address: str = ""
    postcode: str = ""
    city: str = ""
    phone: Optional[str] = None
    contact: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    types: List[str] = field(default_factory=list)
    layer_url: Optional[str] = None
    bbox: Optional[List[float]] = None
    regions: List[Region] = field(default_factory=list)
    image_url: Optional[str] = None
    logo_url: Optional[str] = None
    public_required: Optional[bool] = None
    clicks: Optional[int] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)


# ---------------------------------------------------------------------------
# GraphQL query fragments
# ---------------------------------------------------------------------------

OPERATOR_QUERY_BASIC = """
query ($id: ID!) {
  vnb_vnb(id: $id) {
    _id
    name
    address
    postcode
    city
    phone
    contact
    website
    layerUrl
    bbox
    regions {
      _id
      name
    }
  }
}
"""

OPERATOR_QUERY_DETAILED = """
query ($id: ID!) {
  vnb_vnb(id: $id) {
    _id
    name
    types
    image {
      url
    }
    logo {
      url
    }
    layerUrl
    bbox
    description
    address
    postcode
    city
    phone
    contact
    website
    publicRequired
    clicks
    regions {
      _id
      name
    }
    services {
      type {
        _id
        type
        name
        title
        description
      }
      title
    }
    documents {
      _id
      name
      type
      url
    }
  }
}
"""


class VNBDigitalClient:
    """
    Client for accessing vnbdigital.de grid operator data.

    This client uses the vnbdigital.de GraphQL gateway to look up
    Verteilnetzbetreiber (grid operators) by their BDEW code / ID.

    Args:
        api_url: The GraphQL API endpoint URL.
        timeout: HTTP request timeout in seconds.

    Example::

        client = VNBDigitalClient()
        operator = client.get_operator("179")
        print(operator.name, operator.city)
    """

    DEFAULT_API_URL = "https://www.vnbdigital.de/gateway/graphql"

    def __init__(
        self,
        api_url: Optional[str] = None,
        timeout: int = 30,
    ) -> None:
        """Initialize the vnbdigital client."""
        self.api_url = api_url or self.DEFAULT_API_URL
        self.timeout = timeout

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _execute(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a GraphQL query and return the ``data`` payload.

        Raises:
            ConnectionError: On network / HTTP errors.
            RuntimeError: When the GraphQL response contains errors.
        """
        payload: Dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables

        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ConnectionError(f"HTTP request failed: {exc}") from exc

        result = response.json()

        if "errors" in result:
            messages = "; ".join(e.get("message", str(e)) for e in result["errors"])
            raise RuntimeError(f"GraphQL errors: {messages}")

        data: Dict[str, Any] = result.get("data", {})
        return data

    @staticmethod
    def _parse_operator(raw: Dict[str, Any]) -> Operator:
        """Convert the raw ``vnb_vnb`` dict into an :class:`Operator`."""
        return Operator(
            id=raw["_id"],
            name=raw.get("name", ""),
            address=raw.get("address", ""),
            postcode=raw.get("postcode", ""),
            city=raw.get("city", ""),
            phone=raw.get("phone"),
            contact=raw.get("contact"),
            website=raw.get("website"),
            description=raw.get("description"),
            types=raw.get("types", []),
            layer_url=raw.get("layerUrl"),
            bbox=raw.get("bbox"),
            regions=[Region(id=r["_id"], name=r["name"]) for r in raw.get("regions", [])],
            image_url=raw.get("image", {}).get("url") if raw.get("image") else None,
            logo_url=raw.get("logo", {}).get("url") if raw.get("logo") else None,
            public_required=raw.get("publicRequired"),
            clicks=raw.get("clicks"),
            raw=raw,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_operator(self, operator_id: str) -> Optional[Operator]:
        """
        Fetch basic information for a grid operator by ID.

        Args:
            operator_id: BDEW code or vnbdigital ID of the operator
                (e.g. ``"179"``).

        Returns:
            An :class:`Operator` instance, or ``None`` if the ID is unknown.

        Raises:
            ConnectionError: On network / HTTP errors.
            RuntimeError: On GraphQL-level errors.
        """
        data = self._execute(OPERATOR_QUERY_BASIC, variables={"id": operator_id})
        vnb = data.get("vnb_vnb")
        if vnb is None:
            return None
        return self._parse_operator(vnb)

    def get_operator_details(self, operator_id: str) -> Optional[Operator]:
        """
        Fetch detailed information for a grid operator by ID.

        This returns the same :class:`Operator` object but with additional
        fields populated (``types``, ``description``, ``image_url``,
        ``logo_url``, ``clicks``, etc.).  The full raw response is available
        in :attr:`Operator.raw`.

        Args:
            operator_id: BDEW code or vnbdigital ID of the operator.

        Returns:
            An :class:`Operator` instance, or ``None`` if the ID is unknown.
        """
        data = self._execute(OPERATOR_QUERY_DETAILED, variables={"id": operator_id})
        vnb = data.get("vnb_vnb")
        if vnb is None:
            return None
        return self._parse_operator(vnb)

    def get_operators(self, operator_ids: List[str]) -> Dict[str, Optional[Operator]]:
        """
        Fetch multiple operators by their IDs.

        This is a convenience wrapper that calls :meth:`get_operator` for
        each ID.

        Args:
            operator_ids: List of BDEW codes / vnbdigital IDs.

        Returns:
            Dict mapping each requested ID to an :class:`Operator` or ``None``.
        """
        results: Dict[str, Optional[Operator]] = {}
        for oid in operator_ids:
            results[oid] = self.get_operator(oid)
        return results
