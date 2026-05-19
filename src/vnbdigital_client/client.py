"""
Main client for vnbdigital.de API.

This module provides the VNBDigitalClient class which abstracts GraphQL operations
to provide a simple Python API for accessing vnbdigital.de grid operator data.

The vnbdigital.de API uses GraphQL with the query ``vnb_vnb(id: $id)`` to look up
grid operators (Verteilnetzbetreiber) by their BDEW code.
"""

from dataclasses import dataclass, field
import os
from typing import Any, Dict, List, Optional

import requests


@dataclass
class Region:
    """A geographical region associated with a grid operator."""

    id: str
    name: str


@dataclass
class Postcode:
    """A postal code area."""

    id: str
    name: str
    code: str
    bbox: Optional[List[float]] = None
    layer_url: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass
class SearchResult:
    """A search result from vnb_search query.

    Attributes:
        id: Internal vnbdigital ID.
        title: Main title/name of the result.
        subtitle: Subtitle or additional information.
        logo_url: URL of the logo image.
        url: URL link to the resource.
        type: Type of the result (e.g., "postcode", "vnb", "region").
        raw: The full raw API response dict.
    """

    id: str
    title: str
    subtitle: str = ""
    logo_url: Optional[str] = None
    url: Optional[str] = None
    type: str = ""
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)


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

SEARCH_POSTCODE_QUERY = """
query ($code: String!) {
  vnb_postcodes(code: $code) {
    _id
    name
    code
    bbox
    layerUrl
  }
}
"""

VNB_SEARCH_QUERY = """
query ($searchTerm: String!) {
  vnb_search(searchTerm: $searchTerm) {
    _id
    title
    subtitle
    logo {
      url
    }
    url
    type
  }
}
"""

DETAIL_QUERY = """
fragment vnb_Region on vnb_Region {
  _id
  name
  logo {
    url
  }
  bbox
  layerUrl
  slug
  vnbs {
    _id
  }
}

fragment vnb_VNB on vnb_VNB {
  _id
  name
  logo {
    url
  }
  services {
    type {
      name
      type
    }
    activated
  }
  bbox
  layerUrl
  types
  voltageTypes
}

query (
  $communityId: ID
  $coordinates: String
  $postcodeId: ID
  $filter: vnb_FilterInput
  $withCommunity: Boolean = false
  $withCoordinates: Boolean = false
  $withPostcode: Boolean = false
) {
  vnb_coordinates(coordinates: $coordinates) @include(if: $withCoordinates) {
    geometry
    regions(filter: $filter) {
      ...vnb_Region
    }
    vnbs(filter: $filter) {
      ...vnb_VNB
    }
  }
  vnb_community(id: $communityId) @include(if: $withCommunity) {
    _id
    name
    bbox
    layerUrl
    regions(filter: $filter) {
      ...vnb_Region
    }
    vnbs(filter: $filter) {
      ...vnb_VNB
    }
  }
  vnb_postcode(id: $postcodeId) @include(if: $withPostcode) {
    _id
    name
    code
    bbox
    layerUrl
    regions(filter: $filter) {
      ...vnb_Region
    }
    vnbs(filter: $filter) {
      ...vnb_VNB
    }
  }
}
"""

# Keep old name as alias for backward compatibility
SEARCH_BY_POSTCODE_QUERY = DETAIL_QUERY


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

    def search(self, search_term: str) -> List[SearchResult]:
        """
        Search vnbdigital.de using the unified search API.

        This uses the same search endpoint as the vnbdigital.de website,
        which can find postcodes, operators, regions, and other entities.

        Args:
            search_term: The search term (e.g. postal code, operator name, etc.).

        Returns:
            List of :class:`SearchResult` objects matching the search.

        Example::

            client = VNBDigitalClient()
            results = client.search("90158")
            for result in results:
                print(f"{result.type}: {result.title}")
        """
        data = self._execute(VNB_SEARCH_QUERY, variables={"searchTerm": search_term})
        search_results = data.get("vnb_search", [])

        results = []
        for item in search_results:
            results.append(
                SearchResult(
                    id=item["_id"],
                    title=item.get("title", ""),
                    subtitle=item.get("subtitle", ""),
                    logo_url=item.get("logo", {}).get("url") if item.get("logo") else None,
                    url=item.get("url"),
                    type=item.get("type", ""),
                    raw=item,
                )
            )
        return results

    def search_postcode(self, postcode: str) -> List[Postcode]:
        """
        Search for postal code areas by their code.

        Args:
            postcode: The postal code to search for (e.g. "90158").

        Returns:
            List of :class:`Postcode` objects matching the search.
        """
        data = self._execute(SEARCH_POSTCODE_QUERY, variables={"code": postcode})
        postcodes_data = data.get("vnb_postcodes", [])

        results = []
        for pc in postcodes_data:
            results.append(
                Postcode(
                    id=pc["_id"],
                    name=pc.get("name", ""),
                    code=pc.get("code", ""),
                    bbox=pc.get("bbox"),
                    layer_url=pc.get("layerUrl"),
                    raw=pc,
                )
            )
        return results

    def search_by_postcode(
        self,
        postcode_id: str,
        only_nap: bool = False,
        voltage_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Search for network operators by postal code ID.

        Args:
            postcode_id: The internal postal code ID (from :meth:`search_postcode`
                or a ``POSTCODE`` result from :meth:`search`).
            only_nap: Filter for network access points only.
            voltage_types: List of voltage types to filter
                (default: ``["Niederspannung", "Mittelspannung"]``).

        Returns:
            Dict containing postcode info, regions, and vnbs (network operators).
        """
        if voltage_types is None:
            voltage_types = ["Niederspannung", "Mittelspannung"]

        variables = {
            "postcodeId": postcode_id,
            "withPostcode": True,
            "filter": {
                "onlyNap": only_nap,
                "voltageTypes": voltage_types,
                "withRegions": True,
            },
        }

        data = self._execute(DETAIL_QUERY, variables=variables)
        result: Dict[str, Any] = data.get("vnb_postcode", {})
        return result

    def search_by_coordinates(
        self,
        coordinates: str,
        only_nap: bool = False,
        voltage_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Search for network operators by geographic coordinates.

        This uses the same API call as the vnbdigital.de website when a user
        selects a ``LOCATION`` search result (e.g. a street address or district).

        Args:
            coordinates: Latitude/longitude string as returned in the search result
                URL, e.g. ``"49.550954,11.110085"`` (``"lat,lon"`` format).
            only_nap: Filter for network access points only.
            voltage_types: List of voltage types to filter
                (default: ``["Niederspannung", "Mittelspannung"]``).

        Returns:
            Dict with keys ``geometry``, ``regions``, and ``vnbs``.

        Example::

            client = VNBDigitalClient()
            results = client.search("91058 Erlangen - Bruck")
            location = next(r for r in results if r.type == "LOCATION")
            # Extract coordinates from URL, e.g. "/overview?coordinates=49.56,10.99"
            coords = location.url.split("coordinates=")[1].split("&")[0]
            detail = client.search_by_coordinates(coords)
            for vnb in detail.get("vnbs", []):
                print(vnb["name"])
        """
        if voltage_types is None:
            voltage_types = ["Niederspannung", "Mittelspannung"]

        variables = {
            "coordinates": coordinates,
            "withCoordinates": True,
            "filter": {
                "onlyNap": only_nap,
                "voltageTypes": voltage_types,
                "withRegions": True,
            },
        }

        data = self._execute(DETAIL_QUERY, variables=variables)
        result: Dict[str, Any] = data.get("vnb_coordinates", {})
        return result


# ---------------------------------------------------------------------------
# BDEW code lookup (bdew-codes.de API, independent of VNBDigitalClient)
# ---------------------------------------------------------------------------

_BDEW_BASE_URL = "https://bdew-codes.de"
_BDEW_LIST_URL = f"{_BDEW_BASE_URL}/Codenumbers/BDEWCodes/GetCompanyList"
_BDEW_DETAIL_URL = f"{_BDEW_BASE_URL}/Codenumbers/BDEWCodes/GetBdewCodeListOfCompany"
_BDEW_DETAIL_INFO_URL = f"{_BDEW_BASE_URL}/Codenumbers/BDEWCodes/BdewCodeDetailInfo"


def _bdew_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Content-Type": "application/x-www-form-urlencoded"})
    return s


def _bdew_fetch_all_companies(
    session: requests.Session, timeout: int, list_url: str = _BDEW_LIST_URL
) -> List[Dict[str, Any]]:
    probe = session.post(
        list_url,
        data={"jtStartIndex": "0", "jtPageSize": "1", "jtSorting": "Company ASC"},
        timeout=timeout,
    )
    probe.raise_for_status()
    total = probe.json()["TotalRecordCount"]
    resp = session.post(
        list_url,
        data={"jtStartIndex": "0", "jtPageSize": str(total), "jtSorting": "Company ASC"},
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()["Records"]


def _bdew_fetch_market_functions(
    session: requests.Session, company_id: int, timeout: int,
    detail_url: str = _BDEW_DETAIL_URL,
) -> List[Dict[str, Any]]:
    resp = session.post(
        detail_url,
        params={"companyId": company_id},
        data={"jtStartIndex": "0", "jtPageSize": "200"},
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("Result") != "OK":
        return []
    return data.get("Records", [])


def _bdew_build_mf(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": record["Id"],
        "bdew_code": record["BdewCode"],
        "function": record["MarketFunctionName"],
        "contact": record.get("ContactName", ""),
    }


def _bdew_parse_detail_html(html: str) -> Dict[str, Any]:
    """Extract fields from the BdewCodeDetailInfo HTML fragment."""

    def _get(label: str) -> str:
        import re as _re
        m = _re.search(
            rf'<label>{_re.escape(label)}:</label>.*?<(?:div|span)[^>]*>(.*?)</(?:div|span)>',
            html,
            _re.DOTALL,
        )
        if not m:
            return ""
        return _re.sub(r'<[^>]+>', '', m.group(1)).strip()

    return {
        "street": _get("Stra\u00dfe und Hausnummer"),
        "zip": _get("PLZ"),
        "city": _get("Stadt"),
        "website": _get("Internetseite"),
        "salutation": _get("Anrede"),
        "first_name": _get("Vorname"),
        "last_name": _get("Nachname"),
        "phone": _get("Telefonnummer"),
        "fax": _get("Faxnummer"),
        "email": _get("E-Mail-Adresse"),
    }


def lookup_bdew_market_function_detail(
    bdew_id: int, timeout: int = 30, base_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch address and contact details for a single BDEW market function.

    Args:
        bdew_id: The internal ``Id`` of the market function record (from
            ``lookup_bdew_by_company_code`` / ``lookup_bdew_by_market_code``).
        timeout: HTTP timeout in seconds.
        base_url: Base URL for bdew-codes.de (overrides ``BDEW_LOOKUP_URL`` env var).

    Returns:
        Dict with keys ``street``, ``zip``, ``city``, ``website``,
        ``salutation``, ``first_name``, ``last_name``, ``phone``, ``fax``,
        ``email``.
    """
    _base = (base_url or os.environ.get("BDEW_LOOKUP_URL", _BDEW_BASE_URL)).rstrip("/")
    detail_info_url = f"{_base}/Codenumbers/BDEWCodes/BdewCodeDetailInfo"
    sess = _bdew_session()
    sess.headers.update({"Content-Type": "application/json; charset=UTF-8"})
    resp = sess.post(
        detail_info_url,
        params={"bdewId": ""},
        json={"bdewId": bdew_id},
        timeout=timeout,
    )
    resp.raise_for_status()
    return _bdew_parse_detail_html(resp.text)


def lookup_bdew_by_company_code(
    company_uid: int, timeout: int = 30, base_url: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Look up a BDEW company by its CompanyUId (6-7-digit company code).

    Fetches the complete company list from bdew-codes.de, finds the entry with
    the matching ``CompanyUId``, and returns the company together with all its
    market functions.

    Args:
        company_uid: The 6-7-digit BDEW company code (``CompanyUId``), e.g. ``660188``.
        timeout: HTTP timeout in seconds.
        base_url: Base URL for bdew-codes.de (overrides ``BDEW_LOOKUP_URL`` env var).

    Returns:
        ``{"code": int, "name": str, "market_functions": [...]}`` or ``None``.
    """
    _base = (base_url or os.environ.get("BDEW_LOOKUP_URL", _BDEW_BASE_URL)).rstrip("/")
    list_url = f"{_base}/Codenumbers/BDEWCodes/GetCompanyList"
    detail_url = f"{_base}/Codenumbers/BDEWCodes/GetBdewCodeListOfCompany"
    sess = _bdew_session()
    companies = _bdew_fetch_all_companies(sess, timeout, list_url)
    company = next((c for c in companies if c["CompanyUId"] == company_uid), None)
    if company is None:
        return None
    mf_records = _bdew_fetch_market_functions(sess, company["Id"], timeout, detail_url)
    return {
        "code": company["CompanyUId"],
        "name": company["Company"].strip(),
        "market_functions": [_bdew_build_mf(r) for r in mf_records],
    }


def lookup_bdew_by_market_code(
    bdew_code: str, timeout: int = 30, base_url: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Look up a BDEW company by a specific 13-digit market function code.

    Uses the ``filter`` parameter of the GetCompanyList endpoint to find the
    company directly, then returns the company with **only** the matching
    market function entry.

    Args:
        bdew_code: The 13-digit BDEW market function code, e.g. ``"9903445000000"``.
        timeout: HTTP timeout in seconds.
        base_url: Base URL for bdew-codes.de (overrides ``BDEW_LOOKUP_URL`` env var).

    Returns:
        ``{"code": int, "name": str, "market_functions": [<matched entry>]}`` or ``None``.
    """
    _base = (base_url or os.environ.get("BDEW_LOOKUP_URL", _BDEW_BASE_URL)).rstrip("/")
    list_url = f"{_base}/Codenumbers/BDEWCodes/GetCompanyList"
    detail_url = f"{_base}/Codenumbers/BDEWCodes/GetBdewCodeListOfCompany"
    sess = _bdew_session()
    resp = sess.post(
        list_url,
        params={"jtStartIndex": "0", "jtPageSize": "500"},
        data={"filter": bdew_code},
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("Result") != "OK" or not data.get("Records"):
        return None
    company = data["Records"][0]
    mf_records = _bdew_fetch_market_functions(sess, company["Id"], timeout, detail_url)
    match = next((r for r in mf_records if r["BdewCode"] == bdew_code), None)
    if match is None:
        return None
    return {
        "code": company["CompanyUId"],
        "name": company["Company"].strip(),
        "market_functions": [_bdew_build_mf(match)],
    }
