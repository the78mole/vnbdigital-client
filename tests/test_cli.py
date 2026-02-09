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

    def test_main_help(self):
        """Test that main command shows help."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "vnbdigital CLI" in result.output

    @patch("vnbdigital_client.cli.VNBDigitalClient")
    def test_operator_command_table(self, mock_client_class):
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
    def test_operator_command_json(self, mock_client_class):
        """Test operator command with JSON output."""
        mock_client = MagicMock()
        mock_client.get_operator.return_value = SAMPLE_OPERATOR
        mock_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(main, ["operator", "179", "--format", "json"])

        assert result.exit_code == 0
        assert '"_id": "179"' in result.output

    @patch("vnbdigital_client.cli.VNBDigitalClient")
    def test_operator_not_found(self, mock_client_class):
        """Test operator command when operator not found."""
        mock_client = MagicMock()
        mock_client.get_operator.return_value = None
        mock_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(main, ["operator", "99999"])

        assert result.exit_code == 1
        assert "not found" in result.output

    @patch("vnbdigital_client.cli.VNBDigitalClient")
    def test_details_command(self, mock_client_class):
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
    def test_batch_command(self, mock_client_class):
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
