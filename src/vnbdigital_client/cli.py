"""
Command-line interface for vnbdigital-client.

This module provides a CLI tool for looking up grid operators on vnbdigital.de
from the command line.
"""

import json
import sys
from typing import Optional
from urllib.parse import parse_qs, urlparse

import click

from vnbdigital_client import VNBDigitalClient


@click.group()
@click.option("--api-url", envvar="VNBDIGITAL_API_URL", help="GraphQL endpoint URL")
@click.pass_context
def main(ctx: click.Context, api_url: Optional[str]) -> None:
    """
    vnbdigital CLI - Look up grid operators on vnbdigital.de.

    Operators are identified by their BDEW code or vnbdigital ID.

    Set VNBDIGITAL_API_URL to override the default endpoint.
    """
    ctx.ensure_object(dict)
    ctx.obj["client"] = VNBDigitalClient(api_url=api_url)


@main.command()
@click.argument("operator_id")
@click.option("--format", "output_format", type=click.Choice(["json", "table"]), default="table")
@click.pass_context
def operator(ctx: click.Context, operator_id: str, output_format: str) -> None:
    """
    Get basic information for a grid operator.

    OPERATOR_ID is the BDEW code or vnbdigital ID (e.g. "179").

    Example:
        vnbdigital operator 179
    """
    client: VNBDigitalClient = ctx.obj["client"]

    try:
        op = client.get_operator(operator_id)

        if op is None:
            click.echo(f"Operator '{operator_id}' not found.")
            sys.exit(1)

        if output_format == "json":
            click.echo(json.dumps(op.raw, indent=2, ensure_ascii=False))
        else:
            click.echo(f"\n{'=' * 60}")
            click.echo(f"  {op.name}")
            click.echo(f"{'=' * 60}")
            click.echo(f"  ID:       {op.id}")
            if op.address or op.postcode or op.city:
                click.echo(f"  Adresse:  {op.address}, {op.postcode} {op.city}")
            if op.phone:
                click.echo(f"  Telefon:  {op.phone}")
            if op.contact:
                click.echo(f"  Kontakt:  {op.contact}")
            if op.website:
                click.echo(f"  Website:  {op.website}")
            if op.regions:
                names = ", ".join(r.name for r in op.regions)
                click.echo(f"  Regionen: {names}")
            if op.bbox:
                click.echo(f"  BBox:     {op.bbox}")
            click.echo()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("operator_id")
@click.option("--format", "output_format", type=click.Choice(["json", "table"]), default="table")
@click.pass_context
def details(ctx: click.Context, operator_id: str, output_format: str) -> None:
    """
    Get detailed information for a grid operator.

    Returns additional fields like description, types, logo, services, etc.

    Example:
        vnbdigital details 179
    """
    client: VNBDigitalClient = ctx.obj["client"]

    try:
        op = client.get_operator_details(operator_id)

        if op is None:
            click.echo(f"Operator '{operator_id}' not found.")
            sys.exit(1)

        if output_format == "json":
            click.echo(json.dumps(op.raw, indent=2, ensure_ascii=False))
        else:
            click.echo(f"\n{'=' * 60}")
            click.echo(f"  {op.name}")
            click.echo(f"{'=' * 60}")
            click.echo(f"  ID:          {op.id}")
            if op.types:
                click.echo(f"  Typ:         {', '.join(op.types)}")
            if op.description:
                click.echo(f"  Beschreibung: {op.description}")
            if op.address or op.postcode or op.city:
                click.echo(f"  Adresse:     {op.address}, {op.postcode} {op.city}")
            if op.phone:
                click.echo(f"  Telefon:     {op.phone}")
            if op.contact:
                click.echo(f"  Kontakt:     {op.contact}")
            if op.website:
                click.echo(f"  Website:     {op.website}")
            if op.image_url:
                click.echo(f"  Bild:        {op.image_url}")
            if op.logo_url:
                click.echo(f"  Logo:        {op.logo_url}")
            if op.regions:
                names = ", ".join(r.name for r in op.regions)
                click.echo(f"  Regionen:    {names}")
            if op.bbox:
                click.echo(f"  BBox:        {op.bbox}")
            if op.clicks is not None:
                click.echo(f"  Aufrufe:     {op.clicks}")
            # Services
            services = op.raw.get("services", [])
            if services:
                click.echo(f"\n  Dienste ({len(services)}):")
                for svc in services:
                    title = svc.get("title", svc.get("type", {}).get("name", "N/A"))
                    click.echo(f"    - {title}")
            # Documents
            documents = op.raw.get("documents", [])
            if documents:
                click.echo(f"\n  Dokumente ({len(documents)}):")
                for doc in documents:
                    click.echo(f"    - {doc.get('name', 'N/A')} ({doc.get('type', '')})")
            click.echo()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command(name="batch")
@click.argument("operator_ids", nargs=-1, required=True)
@click.option("--format", "output_format", type=click.Choice(["json", "table"]), default="table")
@click.pass_context
def batch_lookup(ctx: click.Context, operator_ids: tuple, output_format: str) -> None:
    """
    Look up multiple operators at once.

    Example:
        vnbdigital batch 179 180 181
    """
    client: VNBDigitalClient = ctx.obj["client"]

    try:
        results = client.get_operators(list(operator_ids))

        if output_format == "json":
            json_out = {}
            for oid, op in results.items():
                json_out[oid] = op.raw if op else None
            click.echo(json.dumps(json_out, indent=2, ensure_ascii=False))
        else:
            found = sum(1 for v in results.values() if v is not None)
            click.echo(f"\nResults: {found}/{len(operator_ids)} operators found\n")
            for oid, op in results.items():
                if op:
                    location = f"{op.postcode} {op.city}".strip()
                    click.echo(f"  [{oid}] {op.name} - {location}")
                else:
                    click.echo(f"  [{oid}] not found")
            click.echo()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("search_term")
@click.option("--format", "output_format", type=click.Choice(["json", "table"]), default="table")
@click.option("--details", is_flag=True, help="Show detailed info for postcode results")
@click.pass_context
def search(ctx: click.Context, search_term: str, output_format: str, details: bool) -> None:
    """
    Search vnbdigital.de for operators, postcodes, regions, etc.

    SEARCH_TERM can be a postal code, operator name, or other search query.

    This uses the same unified search API as the vnbdigital.de website.

    Example:
        vnbdigital search 90158
        vnbdigital search 90158 --details
        vnbdigital search "Stadtwerke"
    """
    client: VNBDigitalClient = ctx.obj["client"]

    try:
        # Use unified search API
        results = client.search(search_term)

        if not results:
            click.echo(f"No results found for '{search_term}'.")
            sys.exit(1)

        if output_format == "json":
            json_out = [r.raw for r in results]
            click.echo(json.dumps(json_out, indent=2, ensure_ascii=False))
        else:
            click.echo(f"\n{'=' * 60}")
            click.echo(f"  Suchergebnisse für: {search_term}")
            click.echo(f"{'=' * 60}\n")

            for result in results:
                type_label = result.type or "Unknown"
                click.echo(f"  [{type_label}] {result.title}")
                if result.subtitle:
                    click.echo(f"    {result.subtitle}")
                if result.url:
                    click.echo(f"    URL: {result.url}")

                if details:
                    _print_details(client, result.type, result.id, result.url)

                click.echo()

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def _print_details(
    client: VNBDigitalClient,
    result_type: str,
    result_id: str,
    result_url: Optional[str],
) -> None:
    """Fetch and print VNB details for a single search result."""
    try:
        if result_type.upper() == "POSTCODE":
            detail = client.search_by_postcode(result_id)
            _print_vnb_summary(detail.get("vnbs", []))
        elif result_type.upper() == "LOCATION" and result_url:
            coords = _extract_coordinates(result_url)
            if coords:
                detail = client.search_by_coordinates(coords)
                _print_vnb_summary(detail.get("vnbs", []))
    except Exception:
        # Silently skip details fetch on error (optional feature)
        pass


def _extract_coordinates(url: str) -> Optional[str]:
    """Extract the coordinates query param from a result URL.

    E.g. ``/overview?coordinates=49.56,10.99&searchType=LOCATION``
    → ``"49.56,10.99"``
    """
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        coords_list = params.get("coordinates")
        return coords_list[0] if coords_list else None
    except Exception:
        return None


def _print_vnb_summary(vnbs: list) -> None:
    """Print a short summary of network operators."""
    if vnbs:
        click.echo(f"    Netzbetreiber: {len(vnbs)}")
        for vnb in vnbs[:3]:
            click.echo(f"      - {vnb.get('name', 'N/A')}")
        if len(vnbs) > 3:
            click.echo(f"      ... und {len(vnbs) - 3} weitere")


if __name__ == "__main__":
    main()
