"""
Advanced example showing metadata filtering and batch operations.
"""

from endee_client import EndeeClient
import random

def main():
    client = EndeeClient(base_url="http://localhost:8080")
    
    index_name = "filtered_search"
    dim = 64
    
    print(f"Creating index '{index_name}'...")
    try:
        client.create_index(
            index_name=index_name,
            dim=dim,
            space_type="l2"
        )
    except Exception as e:
        print(f"Note: {e}")
    
    # Insert vectors with rich metadata
    print("\nInserting vectors with metadata...")
    vectors = []
    categories = ["electronics", "clothing", "books", "food", "toys"]
    
    for i in range(50):
        vector = [random.random() for _ in range(dim)]
        vectors.append({
            "id": f"product_{i}",
            "vector": vector,
            "metadata": {
                "category": categories[i % len(categories)],
                "price": round(random.uniform(10, 1000), 2),
                "rating": round(random.uniform(1, 5), 1),
                "in_stock": random.choice([True, False])
            }
        })
    
    # Insert in batches of 10
    batch_size = 10
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        client.insert_vectors(index_name, batch)
        print(f"  Inserted batch {i // batch_size + 1}")
    
    print(f"Total inserted: {len(vectors)} vectors")
    
    # Search with different filters
    query_vector = [random.random() for _ in range(dim)]
    
    print("\n1. Search for electronics with rating > 4.0:")
    results = client.search_vectors(
        index_name=index_name,
        vector=query_vector,
        k=5,
        filter_expr="category == 'electronics' AND rating > 4.0"
    )
    print_results(results)
    
    print("\n2. Search for in-stock items under $100:")
    results = client.search_vectors(
        index_name=index_name,
        vector=query_vector,
        k=5,
        filter_expr="in_stock == true AND price < 100"
    )
    print_results(results)
    
    print("\n3. Search for books or toys:")
    results = client.search_vectors(
        index_name=index_name,
        vector=query_vector,
        k=5,
        filter_expr="category == 'books' OR category == 'toys'"
    )
    print_results(results)
    
    # Get specific vectors
    print("\n4. Retrieve specific vectors by ID:")
    vectors_data = client.get_vector(
        index_name,
        ["product_0", "product_5", "product_10"]
    )
    print(f"Retrieved {len(vectors_data.get('vectors', []))} vectors")
    
    # Delete some vectors
    print("\n5. Delete vectors with low ratings:")
    # First, search for low-rated items
    low_rated = client.search_vectors(
        index_name=index_name,
        vector=query_vector,
        k=100,
        filter_expr="rating < 2.5"
    )
    
    ids_to_delete = [r['id'] for r in low_rated.get('results', [])]
    if ids_to_delete:
        client.delete_vectors(index_name, ids_to_delete)
        print(f"Deleted {len(ids_to_delete)} low-rated vectors")
    else:
        print("No low-rated vectors found")
    
    # Check index info
    info = client.get_index_info(index_name)
    print(f"\nFinal index stats:")
    print(f"  Total vectors: {info.get('count', 'N/A')}")
    
    # Clean up
    print(f"\nCleaning up...")
    client.delete_index(index_name)
    print("Done!")

def print_results(results):
    """Helper function to print search results"""
    for r in results.get('results', [])[:5]:
        print(f"  - {r['id']}: distance={r['distance']:.4f}")

if __name__ == "__main__":
    main()
