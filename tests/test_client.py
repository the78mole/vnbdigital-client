"""Tests for vnbdigital_client module."""

from unittest.mock import MagicMock, patch

import pytest

from vnbdigital_client import Operator, Region, VNBDigitalClient

SAMPLE_VNB_BASIC = {
    "_id": "179",
    "name": "Netz Lübeck GmbH",
    "address": "Geniner Str. 80",
    "postcode": "23560",
    "city": "Lübeck",
    "phone": "+49 451 888-0",
    "contact": "info@netz-luebeck.de",
    "website": "https://www.netz-luebeck.de",
    "layerUrl": "https://www.vnbdigital.de/geoserver/vnb_179/wms",
    "bbox": [10.6, 53.7, 10.9, 54.0],
    "regions": [
        {"_id": "r1", "name": "Schleswig-Holstein"},
    ],
}

SAMPLE_VNB_DETAILED = {
    **SAMPLE_VNB_BASIC,
    "types": ["Strom"],
    "description": "Netzbetreiber in Lübeck",
    "image": {"url": "https://example.com/image.jpg"},
    "logo": {"url": "https://example.com/logo.png"},
    "publicRequired": True,
    "clicks": 42,
    "services": [
        {
            "type": {
                "_id": "s1",
                "type": "strom",
                "name": "Strom",
                "title": "Stromversorgung",
                "description": "Netzanschluss",
            },
            "title": "Stromversorgung",
        }
    ],
    "documents": [
        {"_id": "d1", "name": "Preisblatt", "type": "pdf", "url": "https://example.com/doc.pdf"}
    ],
}


class TestVNBDigitalClient:
    """Test cases for VNBDigitalClient."""

    def test_client_initialization(self):
        """Test that client initialises with default URL."""
        client = VNBDigitalClient()
        assert client.api_url == VNBDigitalClient.DEFAULT_API_URL
        assert client.timeout == 30

    def test_client_with_custom_url(self):
        """Test that client can be initialised with a custom URL."""
        custom_url = "https://custom.api/graphql"
        client = VNBDigitalClient(api_url=custom_url)
        assert client.api_url == custom_url

    def test_client_with_custom_timeout(self):
        """Test that client can be initialised with a custom timeout."""
        client = VNBDigitalClient(timeout=60)
        assert client.timeout == 60

    @patch("vnbdigital_client.client.requests.post")
    def test_get_operator(self, mock_post):
        """Test get_operator returns an Operator."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"vnb_vnb": SAMPLE_VNB_BASIC}}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        client = VNBDigitalClient()
        op = client.get_operator("179")

        assert op is not None
        assert isinstance(op, Operator)
        assert op.id == "179"
        assert op.name == "Netz Lübeck GmbH"
        assert op.city == "Lübeck"
        assert op.postcode == "23560"
        assert op.website == "https://www.netz-luebeck.de"
        assert len(op.regions) == 1
        assert op.regions[0].name == "Schleswig-Holstein"

    @patch("vnbdigital_client.client.requests.post")
    def test_get_operator_not_found(self, mock_post):
        """Test get_operator returns None for unknown ID."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"vnb_vnb": None}}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        client = VNBDigitalClient()
        op = client.get_operator("99999")
        assert op is None

    @patch("vnbdigital_client.client.requests.post")
    def test_get_operator_details(self, mock_post):
        """Test get_operator_details returns detailed Operator."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"vnb_vnb": SAMPLE_VNB_DETAILED}}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        client = VNBDigitalClient()
        op = client.get_operator_details("179")

        assert op is not None
        assert op.types == ["Strom"]
        assert op.description == "Netzbetreiber in Lübeck"
        assert op.image_url == "https://example.com/image.jpg"
        assert op.logo_url == "https://example.com/logo.png"
        assert op.clicks == 42
        assert op.public_required is True
        assert "services" in op.raw
        assert "documents" in op.raw

    @patch("vnbdigital_client.client.requests.post")
    def test_get_operators_batch(self, mock_post):
        """Test get_operators looks up multiple IDs."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        # First call returns operator, second returns None
        mock_response.json.side_effect = [
            {"data": {"vnb_vnb": SAMPLE_VNB_BASIC}},
            {"data": {"vnb_vnb": None}},
        ]
        mock_post.return_value = mock_response

        client = VNBDigitalClient()
        results = client.get_operators(["179", "00000"])

        assert results["179"] is not None
        assert results["179"].name == "Netz Lübeck GmbH"
        assert results["00000"] is None

    @patch("vnbdigital_client.client.requests.post")
    def test_graphql_error_raises(self, mock_post):
        """Test that GraphQL errors raise RuntimeError."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"errors": [{"message": "Something went wrong"}]}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        client = VNBDigitalClient()
        with pytest.raises(RuntimeError, match="GraphQL errors"):
            client.get_operator("179")

    @patch("vnbdigital_client.client.requests.post")
    def test_connection_error_raises(self, mock_post):
        """Test that HTTP errors raise ConnectionError."""
        import requests as req

        mock_post.side_effect = req.ConnectionError("No route to host")

        client = VNBDigitalClient()
        with pytest.raises(ConnectionError, match="HTTP request failed"):
            client.get_operator("179")


class TestOperatorDataclass:
    """Test Operator and Region dataclasses."""

    def test_region_creation(self):
        r = Region(id="r1", name="Bayern")
        assert r.id == "r1"
        assert r.name == "Bayern"

    def test_operator_defaults(self):
        op = Operator(id="1", name="Test")
        assert op.address == ""
        assert op.types == []
        assert op.regions == []
        assert op.raw == {}
        assert op.bbox is None
