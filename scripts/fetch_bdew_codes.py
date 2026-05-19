#!/usr/bin/env python3
"""
fetch_bdew_codes.py - Download the complete BDEW company list with all market functions.

For each company the script fetches:
  - Company name and BDEW company code (CompanyUId)
  - All market function entries (BdewCode, MarketFunctionName, ContactName)

Data source: https://bdew-codes.de/Codenumbers/BDEWCodes/CodeOverview

Usage:
    python scripts/fetch_bdew_codes.py
    python scripts/fetch_bdew_codes.py --output bdew_full.json
    python scripts/fetch_bdew_codes.py --output bdew_full.json --workers 20
    uv run python scripts/fetch_bdew_codes.py -o bdew_full.json
"""

import argparse
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

LIST_URL = "https://bdew-codes.de/Codenumbers/BDEWCodes/GetCompanyList"
DETAIL_URL = "https://bdew-codes.de/Codenumbers/BDEWCodes/GetBdewCodeListOfCompany"


def _new_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Content-Type": "application/x-www-form-urlencoded"})
    return s


def fetch_all_companies(timeout: int = 30) -> list:
    """Fetch the full company list in a single request."""
    session = _new_session()

    probe = session.post(
        LIST_URL,
        data={"jtStartIndex": "0", "jtPageSize": "1", "jtSorting": "Company ASC"},
        timeout=timeout,
    )
    probe.raise_for_status()
    total = probe.json()["TotalRecordCount"]

    response = session.post(
        LIST_URL,
        data={"jtStartIndex": "0", "jtPageSize": str(total), "jtSorting": "Company ASC"},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()["Records"]


# Thread-local sessions so each worker has its own TCP connection pool.
_local = threading.local()


def _session() -> requests.Session:
    if not hasattr(_local, "session"):
        _local.session = _new_session()
    return _local.session


def fetch_market_functions(company_id: int, timeout: int = 30) -> list:
    """Fetch all market function entries for one company (by internal Id)."""
    response = _session().post(
        DETAIL_URL,
        params={"companyId": company_id},
        data={"jtStartIndex": "0", "jtPageSize": "200"},
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    if data.get("Result") != "OK":
        return []
    return data.get("Records", [])


def build_entry(company: dict, market_functions: list) -> dict:
    return {
        "code": company["CompanyUId"],
        "name": company["Company"].strip(),
        "market_functions": [
            {
                "bdew_code": mf["BdewCode"],
                "function": mf["MarketFunctionName"],
                "contact": mf.get("ContactName", ""),
            }
            for mf in market_functions
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download BDEW company list with all market functions as JSON."
    )
    parser.add_argument(
        "--output", "-o",
        default="-",
        help="Output file path. Use '-' for stdout (default).",
    )
    parser.add_argument(
        "--workers", "-w",
        type=int,
        default=15,
        help="Number of parallel HTTP workers (default: 15).",
    )
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=30,
        help="HTTP timeout in seconds (default: 30).",
    )
    args = parser.parse_args()

    # --- Step 1: company list ---
    print("Lade Unternehmensliste …", file=sys.stderr)
    try:
        companies = fetch_all_companies(timeout=args.timeout)
    except Exception as exc:
        print(f"Fehler beim Laden der Unternehmensliste: {exc}", file=sys.stderr)
        sys.exit(1)

    total = len(companies)
    print(f"{total} Unternehmen gefunden. Lade Marktfunktionen …", file=sys.stderr)

    # --- Step 2: market functions (parallel) ---
    results: list = [None] * total
    done = 0
    errors = 0

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_idx = {
            executor.submit(fetch_market_functions, c["Id"], args.timeout): i
            for i, c in enumerate(companies)
        }

        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            company = companies[idx]
            try:
                mfs = future.result()
            except Exception as exc:
                mfs = []
                errors += 1
                print(f"  Warnung: {company['Company'].strip()} – {exc}", file=sys.stderr)

            results[idx] = build_entry(company, mfs)
            done += 1
            if done % 250 == 0 or done == total:
                print(f"  {done}/{total} …", file=sys.stderr)

    # Sort alphabetically by name
    results.sort(key=lambda x: x["name"].lower())

    if errors:
        print(f"\n{errors} Fehler beim Laden von Marktfunktionen.", file=sys.stderr)

    # --- Step 3: output ---
    output = json.dumps(results, indent=2, ensure_ascii=False)

    if args.output == "-":
        print(output)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"\nGespeichert: {args.output}  ({len(results)} Einträge)", file=sys.stderr)


if __name__ == "__main__":
    main()
