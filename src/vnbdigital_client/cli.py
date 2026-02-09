"""
Command-line interface for vnbdigital-client.

This module provides a CLI tool for looking up grid operators on vnbdigital.de
from the command line.
"""

import json
import sys
from typing import Optional

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
@click.argument("postcode")
@click.option("--format", "output_format", type=click.Choice(["json", "table"]), default="table")
@click.pass_context
def search(ctx: click.Context, postcode: str, output_format: str) -> None:
    """
    Search for network operators by postal code.

    POSTCODE is the postal code to search for (e.g. "90158").

    Example:
        vnbdigital search 90158
    """
    client: VNBDigitalClient = ctx.obj["client"]

    try:
        # First, find the postcode ID
        postcodes = client.search_postcode(postcode)

        if not postcodes:
            click.echo(f"Postal code '{postcode}' not found.")
            sys.exit(1)

        # Use the first matching postcode
        pc = postcodes[0]

        # Search for network operators in this postcode area
        result = client.search_by_postcode(pc.id)

        if not result:
            click.echo(f"No data found for postal code '{postcode}'.")
            sys.exit(1)

        if output_format == "json":
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            click.echo(f"\n{'=' * 60}")
            click.echo(f"  Postleitzahl: {result.get('code', postcode)} - {result.get('name', '')}")
            click.echo(f"{'=' * 60}")

            # Display regions
            regions = result.get("regions", [])
            if regions:
                click.echo(f"\n  Regionen ({len(regions)}):")
                for region in regions:
                    click.echo(f"    - {region.get('name', 'N/A')}")

            # Display network operators (VNBs)
            vnbs = result.get("vnbs", [])
            if vnbs:
                click.echo(f"\n  Netzbetreiber ({len(vnbs)}):")
                for vnb in vnbs:
                    name = vnb.get("name", "N/A")
                    types = vnb.get("types", [])
                    type_str = f" ({', '.join(types)})" if types else ""
                    click.echo(f"    - {name}{type_str}")
                    
                    # Show voltage types if available
                    voltage_types = vnb.get("voltageTypes", [])
                    if voltage_types:
                        click.echo(f"      Spannungsebenen: {', '.join(voltage_types)}")
            else:
                click.echo("\n  Keine Netzbetreiber gefunden.")

            click.echo()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
