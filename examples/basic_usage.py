"""
Example usage of vnbdigital-client.

This script demonstrates basic usage of the vnbdigital_client library.
"""

from vnbdigital_client import VNBDigitalClient


def main():
    """Main example function."""
    # Initialize the client
    # You can pass api_url and api_key if needed
    client = VNBDigitalClient()

    print("=== vnbdigital-client Example ===\n")

    # Example 1: Search for items
    print("1. Searching for items...")
    try:
        results = client.search("historical", limit=5)
        print(f"   Found {len(results)} results:")
        for i, item in enumerate(results, 1):
            print(f"   {i}. {item.get('title', 'N/A')}")
    except Exception as e:
        print(f"   Error during search: {e}")

    print()

    # Example 2: List collections
    print("2. Listing collections...")
    try:
        collections = client.list_collections()
        print(f"   Found {len(collections)} collections:")
        for i, collection in enumerate(collections[:3], 1):
            print(
                f"   {i}. {collection.get('name', 'N/A')} ({collection.get('itemCount', 0)} items)"
            )
    except Exception as e:
        print(f"   Error listing collections: {e}")

    print()

    # Example 3: Get a specific item (this will likely fail without a valid ID)
    print("3. Getting a specific item...")
    try:
        item = client.get_item("example-id")
        if item:
            print(f"   Title: {item.get('title', 'N/A')}")
            print(f"   Description: {item.get('description', 'N/A')[:100]}...")
        else:
            print("   Item not found (expected - example ID)")
    except Exception as e:
        print(f"   Error getting item: {e}")

    print("\n=== Example Complete ===")


if __name__ == "__main__":
    main()
