"""
Command-line interface for vnbdigital-client.

This module provides a CLI tool for looking up grid operators on vnbdigital.de
from the command line.
"""

import json
import sys
from typing import Optional, cast
from urllib.parse import parse_qs, urlparse

import click

from vnbdigital_client import VNBDigitalClient
from vnbdigital_client.client import (
    lookup_bdew_by_company_code,
    lookup_bdew_by_market_code,
    lookup_bdew_market_function_detail,
)


@click.group()
@click.option("--api-url", envvar="VNBDIGITAL_API_URL", help="GraphQL endpoint URL")
@click.pass_context
def main(ctx: click.Context, api_url: Optional[str]) -> None:
    """
    vnbdigital CLI - Look up grid operators on vnbdigital.de.

    Operators are identified by their BDEW code or vnbdigital ID.

    \b
    Environment variables:
      VNBDIGITAL_API_URL   Override the vnbdigital.de GraphQL endpoint
      BDEW_LOOKUP_URL      Override the bdew-codes.de base URL (used by: bdew)
    """
    ctx.ensure_object(dict)
    ctx.obj["client"] = VNBDigitalClient(api_url=api_url)


@main.command()
@click.argument("operator_id")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "table"]),
    default="table",
    help="Output format: 'table' (default) or 'json'.",
)
@click.option(
    "--json", "-j", "json_flag", is_flag=True, help="JSON output (shorthand for --format json)."
)
@click.pass_context
def operator(ctx: click.Context, operator_id: str, output_format: str, json_flag: bool) -> None:
    """
    Get basic information for a grid operator.

    OPERATOR_ID is the BDEW code or vnbdigital ID (e.g. "179").

    \b
    Options:
      --format [json|table]  Output format (default: table)
      -j, --json             JSON output (shorthand for --format json)

    Examples:

    \b
        vnbdigital operator 179
        vnbdigital operator 179 -j
    """
    client: VNBDigitalClient = ctx.obj["client"]
    if json_flag:
        output_format = "json"

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
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "table"]),
    default="table",
    help="Output format: 'table' (default) or 'json'.",
)
@click.option(
    "--json", "-j", "json_flag", is_flag=True, help="JSON output (shorthand for --format json)."
)
@click.pass_context
def details(ctx: click.Context, operator_id: str, output_format: str, json_flag: bool) -> None:
    """
    Get detailed information for a grid operator.

    Returns additional fields like description, types, logo, services, etc.

    \b
    Options:
      --format [json|table]  Output format (default: table)
      -j, --json             JSON output (shorthand for --format json)

    Examples:

    \b
        vnbdigital details 179
        vnbdigital details 179 -j
    """
    client: VNBDigitalClient = ctx.obj["client"]
    if json_flag:
        output_format = "json"

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
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "table"]),
    default="table",
    help="Output format: 'table' (default) or 'json'.",
)
@click.option(
    "--json", "-j", "json_flag", is_flag=True, help="JSON output (shorthand for --format json)."
)
@click.pass_context
def batch_lookup(
    ctx: click.Context, operator_ids: tuple, output_format: str, json_flag: bool
) -> None:
    """
    Look up multiple operators at once.

    \b
    Options:
      --format [json|table]  Output format (default: table)
      -j, --json             JSON output (shorthand for --format json)

    Examples:

    \b
        vnbdigital batch 179 180 181
        vnbdigital batch 179 180 181 -j
    """
    client: VNBDigitalClient = ctx.obj["client"]
    if json_flag:
        output_format = "json"

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
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "table"]),
    default="table",
    help="Output format: 'table' (default) or 'json'.",
)
@click.option(
    "--details",
    "-d",
    is_flag=True,
    help="Resolve and show operators for each result (auto-enabled for 5-digit postcodes).",
)
@click.option(
    "--json",
    "-j",
    "json_flag",
    is_flag=True,
    help="JSON output with full operator details (implies --details).",
)
@click.pass_context
def search(
    ctx: click.Context, search_term: str, output_format: str, details: bool, json_flag: bool
) -> None:
    """
    Search vnbdigital.de for operators, postcodes, regions, etc.

    SEARCH_TERM can be a postal code, operator name, or other search query.
    For 5-digit postcodes, operator details are resolved automatically.

    \b
    Options:
      --format [json|table]  Output format (default: table)
      -d, --details          Resolve operators for each result
      -j, --json             JSON output with full operator details

    Examples:

    \b
        vnbdigital search 97816
        vnbdigital search 97816 -j
        vnbdigital search "Stadtwerke"
        vnbdigital search "Stadtwerke" --details
    """
    client: VNBDigitalClient = ctx.obj["client"]
    if json_flag:
        output_format = "json"
        details = True

    # Automatically resolve operators for pure postcode searches (5-digit number)
    if not details and search_term.isdigit() and len(search_term) == 5:
        details = True

    try:
        # Use unified search API
        results = client.search(search_term)

        if not results:
            click.echo(f"No results found for '{search_term}'.")
            sys.exit(1)

        if output_format == "json":
            json_out = []
            for r in results:
                entry = dict(r.raw)
                if details:
                    if r.type.upper() == "POSTCODE":
                        try:
                            detail = client.search_by_postcode(r.id)
                            entry["vnbs"] = detail.get("vnbs", [])
                        except Exception:
                            pass
                    elif r.type.upper() == "LOCATION" and r.url:
                        coords = _extract_coordinates(r.url)
                        if coords:
                            try:
                                detail = client.search_by_coordinates(coords)
                                entry["vnbs"] = detail.get("vnbs", [])
                            except Exception:
                                pass
                json_out.append(entry)
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


@main.command(name="coordinates")
@click.argument("coords")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "table"]),
    default="table",
    help="Output format: 'table' (default) or 'json'.",
)
@click.option(
    "--voltage",
    "voltage_types",
    multiple=True,
    default=("Niederspannung", "Mittelspannung"),
    show_default=True,
    help="Voltage type filter (can be repeated). E.g. --voltage Niederspannung --voltage Mittelspannung",
)
@click.option("--nap", is_flag=True, help="Filter for network access points (NAP) only.")
@click.option(
    "--json", "-j", "json_flag", is_flag=True, help="JSON output (shorthand for --format json)."
)
@click.pass_context
def coordinates(
    ctx: click.Context,
    coords: str,
    output_format: str,
    voltage_types: tuple,
    nap: bool,
    json_flag: bool,
) -> None:
    """
    Look up network operators for a geographic coordinate.

    COORDS must be a "lat,lon" string, e.g. "49.5510,11.1101".

    \b
    Options:
      --format [json|table]  Output format (default: table)
      --voltage TEXT         Voltage type filter, repeatable
                             (default: Niederspannung, Mittelspannung)
      --nap                  Filter for network access points only
      -j, --json             JSON output (shorthand for --format json)

    Examples:

    \b
        vnbdigital coordinates "49.5510,11.1101"
        vnbdigital coordinates "49.5510,11.1101" -j
        vnbdigital coordinates "49.5510,11.1101" --voltage Niederspannung
        vnbdigital coordinates "49.5510,11.1101" --nap
    """
    client: VNBDigitalClient = ctx.obj["client"]
    if json_flag:
        output_format = "json"

    try:
        result = client.search_by_coordinates(
            coords,
            only_nap=nap,
            voltage_types=list(voltage_types),
        )

        if output_format == "json":
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            vnbs = result.get("vnbs", [])
            regions = result.get("regions", [])
            geometry = result.get("geometry")

            click.echo(f"\n{'=' * 60}")
            click.echo(f"  Koordinaten: {coords}")
            click.echo(f"{'=' * 60}")

            if geometry:
                geo_coords = geometry.get("coordinates", [])
                if geo_coords:
                    click.echo(f"  Punkt:       lon={geo_coords[0]}, lat={geo_coords[1]}")

            if regions:
                region_names = ", ".join(r.get("name", "?") for r in regions)
                click.echo(f"  Regionen:    {region_names}")

            if not vnbs:
                click.echo("  Keine Netzbetreiber gefunden.")
            else:
                click.echo(f"\n  Netzbetreiber ({len(vnbs)}):")
                for vnb in vnbs:
                    name = vnb.get("name", "N/A")
                    types = ", ".join(vnb.get("types", []))
                    voltage = ", ".join(vnb.get("voltageTypes", []))
                    line = f"    - {name}"
                    if types:
                        line += f"  [{types}]"
                    if voltage:
                        line += f"  ({voltage})"
                    click.echo(line)

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
            vnb_id = vnb.get("_id", "N/A")
            click.echo(f"      - [{vnb_id}] {vnb.get('name', 'N/A')}")
        if len(vnbs) > 3:
            click.echo(f"      ... und {len(vnbs) - 3} weitere")


def _resolve_operators(client: VNBDigitalClient, location: str, voltage_type: str) -> list:
    """Resolve operators for a postcode or coordinate string.

    If *location* is a 5-digit number it is treated as a German postal code;
    otherwise it is treated as a ``"lat,lon"`` coordinate string.
    """
    if location.isdigit() and len(location) == 5:
        results = client.search(location)
        postcode_result = next((r for r in results if r.type.upper() == "POSTCODE"), None)
        if not postcode_result:
            return []
        detail = client.search_by_postcode(postcode_result.id, voltage_types=[voltage_type])
        return cast(list, detail.get("vnbs", []))
    else:
        detail = client.search_by_coordinates(location, voltage_types=[voltage_type])
        return cast(list, detail.get("vnbs", []))


def _print_voltage_result(
    vnbs: list, location: str, voltage_label: str, output_format: str
) -> None:
    """Print operators for a voltage-specific lookup."""
    if output_format == "json":
        slim = [{"id": v.get("_id"), "name": v.get("name")} for v in vnbs]
        click.echo(json.dumps(slim, indent=2, ensure_ascii=False))
        return

    click.echo(f"\n{'=' * 60}")
    click.echo(f"  {voltage_label} · {location}")
    click.echo(f"{'=' * 60}")
    if not vnbs:
        click.echo("  Kein Netzbetreiber gefunden.")
    else:
        for vnb in vnbs:
            vnb_id = vnb.get("_id", "N/A")
            name = vnb.get("name", "N/A")
            voltage = ", ".join(vnb.get("voltageTypes", []))
            types = ", ".join(vnb.get("types", []))
            line = f"  [{vnb_id}] {name}"
            if types:
                line += f"  [{types}]"
            if voltage:
                line += f"  ({voltage})"
            click.echo(line)
    click.echo()


@main.command()
@click.argument("location")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "table"]),
    default="table",
    help="Output format: 'table' (default) or 'json'.",
)
@click.option(
    "--json", "-j", "json_flag", is_flag=True, help="JSON output (shorthand for --format json)."
)
@click.pass_context
def nsp(ctx: click.Context, location: str, output_format: str, json_flag: bool) -> None:
    """
    Get Niederspannung (low voltage) operator for a postcode or coordinate.

    LOCATION is either a 5-digit postal code or a "lat,lon" coordinate string.

    \b
    Options:
      --format [json|table]  Output format (default: table)
      -j, --json             JSON output (shorthand for --format json)

    Examples:

    \b
        vnbdigital nsp 97816
        vnbdigital nsp "49.998037,9.58033"
        vnbdigital nsp 97816 -j
    """
    client: VNBDigitalClient = ctx.obj["client"]
    if json_flag:
        output_format = "json"
    try:
        vnbs = _resolve_operators(client, location, "Niederspannung")
        _print_voltage_result(vnbs, location, "Niederspannung", output_format)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("location")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "table"]),
    default="table",
    help="Output format: 'table' (default) or 'json'.",
)
@click.option(
    "--json", "-j", "json_flag", is_flag=True, help="JSON output (shorthand for --format json)."
)
@click.pass_context
def msp(ctx: click.Context, location: str, output_format: str, json_flag: bool) -> None:
    """
    Get Mittelspannung (medium voltage) operator for a postcode or coordinate.

    LOCATION is either a 5-digit postal code or a "lat,lon" coordinate string.

    \b
    Options:
      --format [json|table]  Output format (default: table)
      -j, --json             JSON output (shorthand for --format json)

    Examples:

    \b
        vnbdigital msp 97816
        vnbdigital msp "49.998037,9.58033"
        vnbdigital msp 97816 -j
    """
    client: VNBDigitalClient = ctx.obj["client"]
    if json_flag:
        output_format = "json"
    try:
        vnbs = _resolve_operators(client, location, "Mittelspannung")
        _print_voltage_result(vnbs, location, "Mittelspannung", output_format)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("query")
@click.option("--json", "-j", "json_flag", is_flag=True, help="JSON output.")
@click.option(
    "--details",
    "-d",
    "details_flag",
    is_flag=True,
    help="Fetch address and contact details for each market function.",
)
@click.option(
    "--bdew-url",
    envvar="BDEW_LOOKUP_URL",
    default=None,
    help="Base URL for bdew-codes.de (default: https://bdew-codes.de).",
)
@click.pass_context
def bdew(
    ctx: click.Context, query: str, json_flag: bool, details_flag: bool, bdew_url: Optional[str]
) -> None:
    """
    Look up a BDEW company or market function by ID.

    QUERY is either a company code (6-7 digits, e.g. 660188) or a 13-digit
    BDEW market function code (e.g. 9903445000000).

    Company code returns all market functions; market function code returns
    only the one matching entry.

    \b
    Options:
      -j, --json     JSON output
      -d, --details  Fetch address and contact details for each market function
      --bdew-url     Override bdew-codes.de base URL (env: BDEW_LOOKUP_URL)

    Examples:

    \b
        vnbdigital bdew 660188
        vnbdigital bdew 9903445000000
        vnbdigital bdew 660188 --details
        vnbdigital bdew 660188 -j
    """
    q = query.strip()

    if not q.isdigit():
        click.echo(f"Error: '{q}' is not a valid numeric BDEW identifier.", err=True)
        sys.exit(2)

    try:
        if len(q) == 13:
            click.echo(f"Suche BDEW-Code {q} …", err=True)
            result = lookup_bdew_by_market_code(q, base_url=bdew_url)
        elif len(q) > 13:
            click.echo(f"Error: '{q}' has more than 13 digits.", err=True)
            sys.exit(2)
        else:
            click.echo(f"Suche Unternehmen {q} …", err=True)
            result = lookup_bdew_by_company_code(int(q), base_url=bdew_url)

        if result is None:
            click.echo("Nicht gefunden.", err=True)
            sys.exit(1)

        if details_flag:
            for mf in result["market_functions"]:
                mf["details"] = lookup_bdew_market_function_detail(mf["id"], base_url=bdew_url)

        if json_flag:
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            click.echo(f"Unternehmen : {result['name']}")
            click.echo(f"Code        : {result['code']}")
            mfs = result["market_functions"]
            if not mfs:
                click.echo("Marktfunktionen: (keine)")
            else:
                click.echo(f"Marktfunktionen ({len(mfs)}):")
                for mf in mfs:
                    contact = f"  – {mf['contact']}" if mf["contact"] else ""
                    click.echo(f"  {mf['bdew_code']}  {mf['function']}{contact}")
                    if details_flag and "details" in mf:
                        d = mf["details"]
                        addr = f"{d['street']}, {d['zip']} {d['city']}".strip(", ")
                        if addr:
                            click.echo(f"    Adresse : {addr}")
                        if d["website"]:
                            click.echo(f"    Website : {d['website']}")
                        name_parts = " ".join(filter(None, [d["first_name"], d["last_name"]]))
                        if name_parts:
                            sal = f" ({d['salutation']})" if d["salutation"] else ""
                            click.echo(f"    Kontakt : {name_parts}{sal}")
                        if d["phone"]:
                            click.echo(f"    Tel     : {d['phone']}")
                        if d["fax"]:
                            click.echo(f"    Fax     : {d['fax']}")
                        if d["email"]:
                            click.echo(f"    E-Mail  : {d['email']}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
