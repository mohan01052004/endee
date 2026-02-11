"""
Basic example demonstrating Endee Python SDK usage.

This example shows how to:
1. Connect to Endee
2. Create an index
3. Insert vectors
4. Search for similar vectors
5. Clean up
"""

from endee_client import EndeeClient
import random

def main():
    # Initialize the client
    print("Connecting to Endee server...")
    client = EndeeClient(base_url="http://localhost:8080")
    
    # Check server health
    health = client.health_check()
    print(f"Server status: {health}")
    
    # Create an index
    index_name = "basic_example"
    dim = 128
    
    print(f"\nCreating index '{index_name}'...")
    try:
        client.create_index(
            index_name=index_name,
            dim=dim,
            space_type="cosine",
            ef_construction=200,
            m=16
        )
        print("Index created successfully!")
    except Exception as e:
        print(f"Note: {e}")
    
    # Insert some vectors
    print(f"\nInserting vectors...")
    vectors = []
    for i in range(10):
        vector = [random.random() for _ in range(dim)]
        vectors.append({
            "id": f"vec_{i}",
            "vector": vector,
            "metadata": {
                "category": f"cat_{i % 3}",
                "index": i
            }
        })
    
    client.insert_vectors(index_name, vectors)
    print(f"Inserted {len(vectors)} vectors")
    
    # Search for similar vectors
    print(f"\nSearching for similar vectors...")
    query_vector = [random.random() for _ in range(dim)]
    
    results = client.search_vectors(
        index_name=index_name,
        vector=query_vector,
        k=5
    )
    
    print(f"Top 5 results:")
    for result in results.get('results', []):
        print(f"  ID: {result['id']}, Distance: {result['distance']:.4f}")
    
    # Get index info
    print(f"\nIndex information:")
    info = client.get_index_info(index_name)
    print(f"  Vectors count: {info.get('count', 'N/A')}")
    
    # Clean up
    print(f"\nCleaning up...")
    client.delete_index(index_name)
    print("Index deleted successfully!")

if __name__ == "__main__":
    main()
