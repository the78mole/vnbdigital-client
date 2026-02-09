"""Tests for CLI module."""

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
                type="postcode",
                url="/postcode/soEbJkxB68ZM6Yvdt",
                raw={},
            ),
            SearchResult(
                id="vnb123",
                title="Stadtwerke Erlangen",
                subtitle="Strom, Gas",
                type="vnb",
                url="/vnb/vnb123",
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
        assert "postcode" in result.output
        assert "vnb" in result.output

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
