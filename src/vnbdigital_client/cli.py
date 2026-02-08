"""
Command-line interface for vnbdigital-client.

This module provides a CLI tool for interacting with the vnbdigital.de database
from the command line.
"""

import json
import sys
from typing import Optional

import click

from vnbdigital_client import VNBDigitalClient


@click.group()
@click.option("--api-url", envvar="VNBDIGITAL_API_URL", help="API endpoint URL")
@click.option("--api-key", envvar="VNBDIGITAL_API_KEY", help="API authentication key")
@click.pass_context
def main(ctx: click.Context, api_url: Optional[str], api_key: Optional[str]) -> None:
    """
    vnbdigital CLI - A command-line tool for accessing vnbdigital.de database.

    Use environment variables VNBDIGITAL_API_URL and VNBDIGITAL_API_KEY
    or pass them as options.
    """
    ctx.ensure_object(dict)
    ctx.obj["client"] = VNBDigitalClient(api_url=api_url, api_key=api_key)


@main.command()
@click.argument("query")
@click.option("--limit", default=10, help="Maximum number of results")
@click.option("--format", "output_format", type=click.Choice(["json", "table"]), default="table")
@click.pass_context
def search(ctx: click.Context, query: str, limit: int, output_format: str) -> None:
    """
    Search for items in the vnbdigital database.

    Example:
        vnbdigital search "historical documents"
    """
    client = ctx.obj["client"]

    try:
        results = client.search(query, limit=limit)

        if output_format == "json":
            click.echo(json.dumps(results, indent=2))
        else:
            if not results:
                click.echo("No results found.")
            else:
                click.echo(f"\nFound {len(results)} results:\n")
                for i, item in enumerate(results, 1):
                    click.echo(f"{i}. {item.get('title', 'N/A')}")
                    click.echo(f"   ID: {item.get('id', 'N/A')}")
                    if item.get("description"):
                        desc = item.get("description")
                        if len(desc) > 100:
                            click.echo(f"   Description: {desc[:100]}...")
                        else:
                            click.echo(f"   Description: {desc}")
                    click.echo(f"   URL: {item.get('url', 'N/A')}")
                    click.echo()
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.argument("item_id")
@click.option("--format", "output_format", type=click.Choice(["json", "table"]), default="table")
@click.pass_context
def get(ctx: click.Context, item_id: str, output_format: str) -> None:
    """
    Get a specific item by ID.

    Example:
        vnbdigital get 12345
    """
    client = ctx.obj["client"]

    try:
        item = client.get_item(item_id)

        if not item:
            click.echo(f"Item with ID '{item_id}' not found.")
            sys.exit(1)

        if output_format == "json":
            click.echo(json.dumps(item, indent=2))
        else:
            click.echo("\nItem Details:\n")
            click.echo(f"ID: {item.get('id', 'N/A')}")
            click.echo(f"Title: {item.get('title', 'N/A')}")
            click.echo(f"Description: {item.get('description', 'N/A')}")
            click.echo(f"URL: {item.get('url', 'N/A')}")
            if item.get("metadata"):
                click.echo(f"Metadata: {json.dumps(item['metadata'], indent=2)}")
            if item.get("createdAt"):
                click.echo(f"Created: {item.get('createdAt')}")
            if item.get("updatedAt"):
                click.echo(f"Updated: {item.get('updatedAt')}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.option("--format", "output_format", type=click.Choice(["json", "table"]), default="table")
@click.pass_context
def collections(ctx: click.Context, output_format: str) -> None:
    """
    List all available collections.

    Example:
        vnbdigital collections
    """
    client = ctx.obj["client"]

    try:
        collections_list = client.list_collections()

        if output_format == "json":
            click.echo(json.dumps(collections_list, indent=2))
        else:
            if not collections_list:
                click.echo("No collections found.")
            else:
                click.echo(f"\nAvailable Collections ({len(collections_list)}):\n")
                for i, collection in enumerate(collections_list, 1):
                    click.echo(f"{i}. {collection.get('name', 'N/A')}")
                    click.echo(f"   ID: {collection.get('id', 'N/A')}")
                    if collection.get("description"):
                        click.echo(f"   Description: {collection.get('description')}")
                    click.echo(f"   Items: {collection.get('itemCount', 'N/A')}")
                    click.echo()
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.argument("collection_id")
@click.option("--limit", default=50, help="Maximum number of items")
@click.option("--format", "output_format", type=click.Choice(["json", "table"]), default="table")
@click.pass_context
def collection(ctx: click.Context, collection_id: str, limit: int, output_format: str) -> None:
    """
    Get items from a specific collection.

    Example:
        vnbdigital collection abc123 --limit 20
    """
    client = ctx.obj["client"]

    try:
        collection_data = client.get_collection(collection_id, limit=limit)

        if not collection_data:
            click.echo(f"Collection with ID '{collection_id}' not found.")
            sys.exit(1)

        if output_format == "json":
            click.echo(json.dumps(collection_data, indent=2))
        else:
            click.echo(f"\nCollection: {collection_data.get('name', 'N/A')}")
            click.echo(f"ID: {collection_data.get('id', 'N/A')}")
            if collection_data.get("description"):
                click.echo(f"Description: {collection_data.get('description')}")

            items = collection_data.get("items", [])
            click.echo(f"\nItems ({len(items)}):\n")
            for i, item in enumerate(items, 1):
                click.echo(f"{i}. {item.get('title', 'N/A')}")
                click.echo(f"   ID: {item.get('id', 'N/A')}")
                if item.get("description"):
                    desc = item.get("description", "")
                    if len(desc) > 100:
                        click.echo(f"   Description: {desc[:100]}...")
                    else:
                        click.echo(f"   Description: {desc}")
                click.echo()
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
