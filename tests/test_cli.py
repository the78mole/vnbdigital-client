"""Tests for CLI module."""

from click.testing import CliRunner
from unittest.mock import patch, Mock
from vnbdigital_client.cli import main


class TestCLI:
    """Test cases for CLI."""

    def test_main_command(self):
        """Test that main command runs."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "vnbdigital CLI" in result.output

    @patch("vnbdigital_client.cli.VNBDigitalClient")
    def test_search_command(self, mock_client_class):
        """Test search command."""
        mock_client = Mock()
        mock_client.search.return_value = [
            {"id": "1", "title": "Test", "description": "Test item", "url": "http://test.com"}
        ]
        mock_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(main, ["search", "test query"])

        assert result.exit_code == 0
        assert "Test" in result.output

    @patch("vnbdigital_client.cli.VNBDigitalClient")
    def test_get_command(self, mock_client_class):
        """Test get command."""
        mock_client = Mock()
        mock_client.get_item.return_value = {
            "id": "123",
            "title": "Test Item",
            "description": "A test item",
        }
        mock_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(main, ["get", "123"])

        assert result.exit_code == 0
        assert "Test Item" in result.output

    @patch("vnbdigital_client.cli.VNBDigitalClient")
    def test_collections_command(self, mock_client_class):
        """Test collections command."""
        mock_client = Mock()
        mock_client.list_collections.return_value = [
            {"id": "1", "name": "Collection 1", "description": "Test", "itemCount": 10}
        ]
        mock_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(main, ["collections"])

        assert result.exit_code == 0
        assert "Collection 1" in result.output
