"""
Example usage of the postal code search functionality.

This script demonstrates how to search for network operators by postal code.
"""

from vnbdigital_client import VNBDigitalClient


def main() -> None:
    """Main example function."""
    client = VNBDigitalClient()

    print("=== Postcode Search Example ===\n")

    # Example: Search by postal code
    postcode = "90158"  # Erlangen-Bruck
    print(f"Searching for network operators in postal code {postcode}...\n")

    try:
        # Step 1: Search for the postcode to get its ID
        postcodes = client.search_postcode(postcode)

        if not postcodes:
            print(f"Postal code {postcode} not found.")
            return

        pc = postcodes[0]
        print(f"Found postcode: {pc.code} - {pc.name}")
        print(f"Postcode ID: {pc.id}\n")

        # Step 2: Get network operators in this postcode area
        result = client.search_by_postcode(pc.id)

        # Display regions
        regions = result.get("regions", [])
        if regions:
            print(f"Regions ({len(regions)}):")
            for region in regions:
                print(f"  - {region.get('name', 'N/A')}")
            print()

        # Display network operators
        vnbs = result.get("vnbs", [])
        if vnbs:
            print(f"Netzbetreiber ({len(vnbs)}):")
            for vnb in vnbs:
                name = vnb.get("name", "N/A")
                types = vnb.get("types", [])
                voltage_types = vnb.get("voltageTypes", [])

                print(f"\n  {name}")
                if types:
                    print(f"    Typ: {', '.join(types)}")
                if voltage_types:
                    print(f"    Spannungsebenen: {', '.join(voltage_types)}")
        else:
            print("No network operators found.")

    except Exception as e:
        print(f"Error: {e}")

    print("\n=== Example completed ===")


if __name__ == "__main__":
    main()
