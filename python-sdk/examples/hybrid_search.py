"""
Example demonstrating hybrid search with dense and sparse vectors.

Hybrid search combines traditional dense vector similarity with sparse
vector representations (like BM25 or TF-IDF) for better retrieval.
"""

from endee_client import EndeeClient
import random

def main():
    client = EndeeClient(base_url="http://localhost:8080")
    
    index_name = "hybrid_search"
    dim = 128
    
    print(f"Creating hybrid index '{index_name}'...")
    try:
        client.create_index(
            index_name=index_name,
            dim=dim,
            space_type="cosine",
            enable_sparse=True  # Enable sparse vector support
        )
        print("Hybrid index created!")
    except Exception as e:
        print(f"Note: {e}")
    
    # Insert vectors with both dense and sparse components
    print("\nInserting hybrid vectors...")
    vectors = []
    
    # Simulate documents with text tokens
    for i in range(20):
        # Dense vector (e.g., from a neural embedding model)
        dense_vector = [random.random() for _ in range(dim)]
        
        # Sparse vector (e.g., BM25 scores for tokens)
        # Format: {token_id: weight}
        num_tokens = random.randint(5, 15)
        sparse_vector = {
            random.randint(0, 10000): round(random.random(), 3)
            for _ in range(num_tokens)
        }
        
        vectors.append({
            "id": f"doc_{i}",
            "vector": dense_vector,
            "sparse_vector": sparse_vector,
            "metadata": {
                "title": f"Document {i}",
                "category": f"cat_{i % 4}"
            }
        })
    
    client.insert_vectors(index_name, vectors)
    print(f"Inserted {len(vectors)} hybrid vectors")
    
    # Perform hybrid search
    print("\n1. Hybrid search (dense + sparse):")
    query_dense = [random.random() for _ in range(dim)]
    query_sparse = {
        random.randint(0, 10000): round(random.random(), 3)
        for _ in range(8)
    }
    
    results = client.search_vectors(
        index_name=index_name,
        vector=query_dense,
        sparse_vector=query_sparse,
        k=5
    )
    
    print("Top 5 hybrid search results:")
    for r in results.get('results', []):
        print(f"  - {r['id']}: distance={r['distance']:.4f}")
    
    # Dense-only search
    print("\n2. Dense-only search:")
    results = client.search_vectors(
        index_name=index_name,
        vector=query_dense,
        k=5
    )
    
    print("Top 5 dense-only results:")
    for r in results.get('results', []):
        print(f"  - {r['id']}: distance={r['distance']:.4f}")
    
    # Clean up
    print("\nCleaning up...")
    client.delete_index(index_name)
    print("Done!")

if __name__ == "__main__":
    main()
