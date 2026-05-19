"""
Example usage of the unified search functionality.

This script demonstrates how to use the unified search API which matches
the vnbdigital.de website's search functionality.
"""

from vnbdigital_client import VNBDigitalClient


def main() -> None:
    """Main example function."""
    client = VNBDigitalClient()

    print("=== Unified Search Example ===\n")

    # Example 1: Search by postal code (like the website)
    search_term = "90158"
    print(f"Searching for '{search_term}'...\n")

    try:
        results = client.search(search_term)

        if not results:
            print(f"No results found for '{search_term}'.")
            return

        print(f"Found {len(results)} result(s):\n")

        for result in results:
            print(f"  Type: {result.type}")
            print(f"  Title: {result.title}")
            if result.subtitle:
                print(f"  Subtitle: {result.subtitle}")
            if result.url:
                print(f"  URL: {result.url}")
            if result.logo_url:
                print(f"  Logo: {result.logo_url}")

            # If it's a postcode result, we can get more details
            if result.type == "postcode":
                print("\n  Getting detailed information for postcode...")
                try:
                    details = client.search_by_postcode(result.id)
                    vnbs = details.get("vnbs", [])
                    if vnbs:
                        print(f"  Netzbetreiber in this area: {len(vnbs)}")
                        for vnb in vnbs[:3]:  # Show first 3
                            print(f"    - {vnb.get('name', 'N/A')}")
                        if len(vnbs) > 3:
                            print(f"    ... und {len(vnbs) - 3} weitere")
                except Exception as e:
                    print(f"  Could not fetch details: {e}")

            print()

    except Exception as e:
        print(f"Error: {e}")

    print("\n=== Example 2: Search by operator name ===\n")

    try:
        results = client.search("Stadtwerke")
        print(f"Found {len(results)} result(s) for 'Stadtwerke':\n")

        for result in results[:5]:  # Show first 5 results
            print(f"  [{result.type}] {result.title}")
            if result.subtitle:
                print(f"    {result.subtitle}")

    except Exception as e:
        print(f"Error: {e}")

    print("\n=== Example completed ===")


if __name__ == "__main__":
    main()
