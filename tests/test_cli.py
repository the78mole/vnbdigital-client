"""Tests for CLI module."""

import json
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from vnbdigital_client.cli import main
from vnbdigital_client.client import Operator, Region

SAMPLE_OPERATOR = Operator(
    id="179",
    name="Netz Lübeck GmbH",
    address="Geniner Str. 80",
    postcode="23560",
    city="Lübeck",
    phone="+49 451 888-0",
    contact="info@netz-luebeck.de",
    website="https://www.netz-luebeck.de",
    regions=[Region(id="r1", name="Schleswig-Holstein")],
    bbox=[10.6, 53.7, 10.9, 54.0],
    raw={
        "_id": "179",
        "name": "Netz Lübeck GmbH",
        "address": "Geniner Str. 80",
        "postcode": "23560",
        "city": "Lübeck",
    },
)


class TestCLI:
    """Test cases for CLI."""

    def test_main_help(self) -> None:
        """Test that main command shows help."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "vnbdigital CLI" in result.output

    @patch("vnbdigital_client.cli.VNBDigitalClient")
    def test_operator_command_table(self, mock_client_class: MagicMock) -> None:
        """Test operator command with table output."""
        mock_client = MagicMock()
        mock_client.get_operator.return_value = SAMPLE_OPERATOR
        mock_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(main, ["operator", "179"])

        assert result.exit_code == 0
        assert "Netz Lübeck GmbH" in result.output
        assert "Lübeck" in result.output
        assert "Schleswig-Holstein" in result.output

    @patch("vnbdigital_client.cli.VNBDigitalClient")
    def test_operator_command_json(self, mock_client_class: MagicMock) -> None:
        """Test operator command with JSON output."""
        mock_client = MagicMock()
        mock_client.get_operator.return_value = SAMPLE_OPERATOR
        mock_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(main, ["operator", "179", "--format", "json"])

        assert result.exit_code == 0
        assert '"_id": "179"' in result.output

    @patch("vnbdigital_client.cli.VNBDigitalClient")
    def test_operator_not_found(self, mock_client_class: MagicMock) -> None:
        """Test operator command when operator not found."""
        mock_client = MagicMock()
        mock_client.get_operator.return_value = None
        mock_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(main, ["operator", "99999"])

        assert result.exit_code == 1
        assert "not found" in result.output

    @patch("vnbdigital_client.cli.VNBDigitalClient")
    def test_details_command(self, mock_client_class: MagicMock) -> None:
        """Test details command."""
        detailed = Operator(
            id="179",
            name="Netz Lübeck GmbH",
            types=["Strom"],
            description="Netzbetreiber in Lübeck",
            clicks=42,
            raw={"_id": "179", "name": "Netz Lübeck GmbH", "services": [], "documents": []},
        )
        mock_client = MagicMock()
        mock_client.get_operator_details.return_value = detailed
        mock_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(main, ["details", "179"])

        assert result.exit_code == 0
        assert "Netz Lübeck GmbH" in result.output
        assert "Strom" in result.output
        assert "42" in result.output

    @patch("vnbdigital_client.cli.VNBDigitalClient")
    def test_batch_command(self, mock_client_class: MagicMock) -> None:
        """Test batch command."""
        mock_client = MagicMock()
        mock_client.get_operators.return_value = {
            "179": SAMPLE_OPERATOR,
            "00000": None,
        }
        mock_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(main, ["batch", "179", "00000"])

        assert result.exit_code == 0
        assert "1/2 operators found" in result.output
        assert "Netz Lübeck GmbH" in result.output
        assert "not found" in result.output

    @patch("vnbdigital_client.cli.VNBDigitalClient")
    def test_search_command_table(self, mock_client_class: MagicMock) -> None:
        """Test search command with table output."""
        from vnbdigital_client.client import SearchResult

        mock_results = [
            SearchResult(
                id="soEbJkxB68ZM6Yvdt",
                title="90158",
                subtitle="Erlangen",
                type="POSTCODE",
                url="/overview?postcodeId=soEbJkxB68ZM6Yvdt",
                raw={},
            ),
            SearchResult(
                id="vnb123",
                title="Stadtwerke Erlangen",
                subtitle="Strom, Gas",
                type="LOCATION",
                url="/overview?coordinates=49.5,11.0&searchType=LOCATION",
                raw={},
            ),
        ]

        mock_client = MagicMock()
        mock_client.search.return_value = mock_results
        mock_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(main, ["search", "90158"])

        assert result.exit_code == 0
        assert "90158" in result.output
        assert "Erlangen" in result.output
        assert "Stadtwerke Erlangen" in result.output
        assert "POSTCODE" in result.output
        assert "LOCATION" in result.output

    @patch("vnbdigital_client.cli.VNBDigitalClient")
    def test_search_command_json(self, mock_client_class: MagicMock) -> None:
        """Test search command with JSON output."""
        from vnbdigital_client.client import SearchResult

        mock_results = [
            SearchResult(
                id="soEbJkxB68ZM6Yvdt",
                title="90158",
                subtitle="Erlangen",
                type="postcode",
                raw={"_id": "soEbJkxB68ZM6Yvdt", "title": "90158"},
            )
        ]

        mock_client = MagicMock()
        mock_client.search.return_value = mock_results
        mock_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(main, ["search", "90158", "--format", "json"])

        assert result.exit_code == 0
        assert '"_id": "soEbJkxB68ZM6Yvdt"' in result.output

    @patch("vnbdigital_client.cli.VNBDigitalClient")
    def test_search_no_results(self, mock_client_class: MagicMock) -> None:
        """Test search command when no results found."""
        mock_client = MagicMock()
        mock_client.search.return_value = []
        mock_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(main, ["search", "99999"])

        assert result.exit_code == 1
        assert "No results found" in result.output

    @patch("vnbdigital_client.cli.VNBDigitalClient")
    def test_search_command_details_location(self, mock_client_class: MagicMock) -> None:
        """Test --details flag calls search_by_coordinates for LOCATION results."""
        from vnbdigital_client.client import SearchResult

        mock_results = [
            SearchResult(
                id="DEGAC00000062876",
                title="91058 Erlangen - Bruck",
                subtitle="Erlangen, Bayern",
                type="LOCATION",
                url="/overview?coordinates=49.569764,10.99452&searchType=LOCATION",
                raw={},
            ),
        ]
        mock_detail = {
            "geometry": "POINT(10.99 49.57)",
            "regions": [],
            "vnbs": [
                {"name": "N-ERGIE Netz GmbH"},
            ],
        }

        mock_client = MagicMock()
        mock_client.search.return_value = mock_results
        mock_client.search_by_coordinates.return_value = mock_detail
        mock_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(main, ["search", "91058 Erlangen - Bruck", "--details"])

        assert result.exit_code == 0
        assert "Netzbetreiber: 1" in result.output
        assert "N-ERGIE Netz GmbH" in result.output
        mock_client.search_by_coordinates.assert_called_once_with("49.569764,10.99452")

    def test_extract_coordinates(self) -> None:
        """Test coordinate extraction from result URLs."""
        from vnbdigital_client.cli import _extract_coordinates

        url = "/overview?coordinates=49.569764,10.99452&searchType=LOCATION"
        assert _extract_coordinates(url) == "49.569764,10.99452"

        # No coordinates param
        assert _extract_coordinates("/overview?postcodeId=abc") is None

        # Invalid URL
        assert _extract_coordinates("") is None

    @patch("vnbdigital_client.cli.VNBDigitalClient")
    def test_search_command_details(self, mock_client_class: MagicMock) -> None:
        """Test search command --details flag triggers search_by_postcode for POSTCODE results."""
        from vnbdigital_client.client import SearchResult

        mock_results = [
            SearchResult(
                id="soEbJkxB68ZM6Yvdt",
                title="91058",
                subtitle="Erlangen",
                type="POSTCODE",  # uppercase as returned by real API
                url="/overview?postcodeId=soEbJkxB68ZM6Yvdt",
                raw={},
            ),
        ]
        mock_detail = {
            "_id": "soEbJkxB68ZM6Yvdt",
            "code": "91058",
            "vnbs": [
                {"name": "Stadtwerke Erlangen"},
                {"name": "N-ERGIE Netz GmbH"},
            ],
        }

        mock_client = MagicMock()
        mock_client.search.return_value = mock_results
        mock_client.search_by_postcode.return_value = mock_detail
        mock_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(main, ["search", "91058", "--details"])

        assert result.exit_code == 0
        assert "Netzbetreiber: 2" in result.output
        assert "Stadtwerke Erlangen" in result.output
        mock_client.search_by_postcode.assert_called_once_with("soEbJkxB68ZM6Yvdt")

    @patch("vnbdigital_client.cli.VNBDigitalClient")
    def test_coordinates_command_table(self, mock_client_class: MagicMock) -> None:
        """Test coordinates command with table output."""
        mock_detail = {
            "geometry": {"type": "Point", "coordinates": [11.1101, 49.5510]},
            "regions": [{"name": "Bayern"}],
            "vnbs": [
                {
                    "name": "N-ERGIE Netz GmbH",
                    "types": ["Strom"],
                    "voltageTypes": ["Niederspannung", "Mittelspannung"],
                },
            ],
        }
        mock_client = MagicMock()
        mock_client.search_by_coordinates.return_value = mock_detail
        mock_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(main, ["coordinates", "49.5510,11.1101"])

        assert result.exit_code == 0
        assert "49.5510,11.1101" in result.output
        assert "Bayern" in result.output
        assert "N-ERGIE Netz GmbH" in result.output
        assert "Strom" in result.output
        mock_client.search_by_coordinates.assert_called_once_with(
            "49.5510,11.1101",
            only_nap=False,
            voltage_types=["Niederspannung", "Mittelspannung"],
        )

    @patch("vnbdigital_client.cli.VNBDigitalClient")
    def test_coordinates_command_json(self, mock_client_class: MagicMock) -> None:
        """Test coordinates command with JSON output."""
        mock_detail = {
            "geometry": {"type": "Point", "coordinates": [11.1101, 49.5510]},
            "regions": [],
            "vnbs": [{"name": "N-ERGIE Netz GmbH", "types": ["Strom"], "voltageTypes": []}],
        }
        mock_client = MagicMock()
        mock_client.search_by_coordinates.return_value = mock_detail
        mock_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(main, ["coordinates", "49.5510,11.1101", "--format", "json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["vnbs"][0]["name"] == "N-ERGIE Netz GmbH"

    @patch("vnbdigital_client.cli.VNBDigitalClient")
    def test_coordinates_command_no_vnbs(self, mock_client_class: MagicMock) -> None:
        """Test coordinates command when no network operators are found."""
        mock_client = MagicMock()
        mock_client.search_by_coordinates.return_value = {"geometry": None, "regions": [], "vnbs": []}
        mock_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(main, ["coordinates", "0.0,0.0"])

        assert result.exit_code == 0
        assert "Keine Netzbetreiber gefunden" in result.output
