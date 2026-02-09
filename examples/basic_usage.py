"""
Example usage of vnbdigital-client.

This script demonstrates basic usage of the vnbdigital_client library
to look up grid operators (Verteilnetzbetreiber) on vnbdigital.de.
"""

from vnbdigital_client import VNBDigitalClient


def main() -> None:
    """Main example function."""
    client = VNBDigitalClient()

    print("=== vnbdigital-client Example ===\n")

    # Example 1: Fetch basic operator info
    print("1. Looking up operator 179 (basic)...")
    try:
        op = client.get_operator("179")
        if op:
            print(f"   Name:    {op.name}")
            print(f"   Adresse: {op.address}, {op.postcode} {op.city}")
            print(f"   Website: {op.website}")
            if op.regions:
                print(f"   Regionen: {', '.join(r.name for r in op.regions)}")
        else:
            print("   Nicht gefunden.")
    except Exception as e:
        print(f"   Fehler: {e}")

    print()

    # Example 2: Fetch detailed operator info
    print("2. Looking up operator 179 (detailliert)...")
    try:
        op = client.get_operator_details("179")
        if op:
            print(f"   Name:         {op.name}")
            print(f"   Beschreibung: {op.description or 'N/A'}")
            print(f"   Typ:          {', '.join(op.types) if op.types else 'N/A'}")
            print(f"   Aufrufe:      {op.clicks}")
            services = op.raw.get("services", [])
            if services:
                titles = [s.get("title", "?") for s in services]
                print(f"   Dienste:      {', '.join(titles)}")
        else:
            print("   Nicht gefunden.")
    except Exception as e:
        print(f"   Fehler: {e}")

    print()

    # Example 3: Batch lookup
    print("3. Batch-Abfrage für IDs 179, 180, 99999...")
    try:
        results = client.get_operators(["179", "180", "99999"])
        for oid, op in results.items():
            if op:
                print(f"   [{oid}] {op.name} - {op.postcode} {op.city}")
            else:
                print(f"   [{oid}] Nicht gefunden")
    except Exception as e:
        print(f"   Fehler: {e}")

    print("\n=== Beispiel abgeschlossen ===")


if __name__ == "__main__":
    main()
