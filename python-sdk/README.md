# Endee Python SDK - Quick Start Guide

The Endee Python SDK provides a simple and intuitive interface to interact with the Endee vector database. This guide will help you get started quickly.

## Installation

### Install from source

```bash
cd python-sdk
pip install -r requirements.txt
pip install -e .
```

### Prerequisites

- Python 3.8 or higher
- A running Endee server (see main README for installation)

## Starting the Endee Server

Before using the Python SDK, you need to have an Endee server running. See the [main README](../README.md) for detailed installation instructions.

**Quick start with Docker:**

```bash
docker run -p 8080:8080 -v endee-data:/data endeeio/endee-server:latest
```

**Or using the install script:**

```bash
./install.sh --release --avx2
./run.sh
```

## Basic Usage

### 1. Connect to Endee

```python
from endee_client import EndeeClient

# Connect to local server (no authentication)
client = EndeeClient(base_url="http://localhost:8080")

# Or with authentication if NDD_AUTH_TOKEN is set
client = EndeeClient(
    base_url="http://localhost:8080",
    auth_token="your_auth_token"
)

# Check server health
health = client.health_check()
print(health)  # {'status': 'ok'}
```

### 2. Create an Index

```python
# Create a new vector index
response = client.create_index(
    index_name="my_vectors",
    dim=128,                    # Vector dimension
    space_type="l2",           # Distance metric: 'l2', 'ip', or 'cosine'
    ef_construction=200,       # HNSW construction parameter
    m=16,                      # HNSW M parameter
    quant_type="none"          # Quantization: 'none', 'scalar', 'product'
)
print(response)
```

### 3. Insert Vectors

```python
# Prepare vectors with metadata
vectors = [
    {
        "id": "vec1",
        "vector": [0.1] * 128,  # 128-dimensional vector
        "metadata": {
            "category": "A",
            "label": "example1"
        }
    },
    {
        "id": "vec2",
        "vector": [0.2] * 128,
        "metadata": {
            "category": "B",
            "label": "example2"
        }
    }
]

# Insert vectors into the index
response = client.insert_vectors("my_vectors", vectors)
print(response)
```

### 4. Search for Similar Vectors

```python
# Search for the 5 most similar vectors
query_vector = [0.15] * 128

results = client.search_vectors(
    index_name="my_vectors",
    vector=query_vector,
    k=5,                        # Number of results
    ef_search=100               # HNSW search parameter (optional)
)

# Print results
for result in results.get('results', []):
    print(f"ID: {result['id']}, Distance: {result['distance']}")
```

### 5. Search with Metadata Filtering

```python
# Search with filter expression
results = client.search_vectors(
    index_name="my_vectors",
    vector=query_vector,
    k=5,
    filter_expr="category == 'A'"  # Filter by metadata
)
```

### 6. Retrieve Vectors by ID

```python
# Get specific vectors by their IDs
vectors = client.get_vector(
    index_name="my_vectors",
    vector_ids=["vec1", "vec2"]
)
print(vectors)
```

### 7. Delete Vectors

```python
# Delete a single vector
client.delete_vector("my_vectors", "vec1")

# Or delete multiple vectors
client.delete_vectors("my_vectors", ["vec1", "vec2"])
```

### 8. Index Management

```python
# List all indexes
indexes = client.list_indexes()
print(indexes)

# Get index information
info = client.get_index_info("my_vectors")
print(info)

# Delete an index
client.delete_index("my_vectors")
```

### 9. Backup and Restore

```python
# Create a backup
client.create_backup("my_vectors")

# List all backups
backups = client.list_backups()
print(backups)

# Restore from backup
client.restore_backup("backup_name")

# Delete a backup
client.delete_backup("backup_name")
```

## Complete Example

Here's a complete example that demonstrates the full workflow:

```python
from endee_client import EndeeClient
import numpy as np

# Initialize client
client = EndeeClient("http://localhost:8080")

# Check server health
print("Server status:", client.health_check())

# Create an index
print("\nCreating index...")
client.create_index(
    index_name="demo_index",
    dim=128,
    space_type="cosine",
    ef_construction=200,
    m=16
)

# Generate and insert sample vectors
print("\nInserting vectors...")
vectors = []
for i in range(100):
    vector = np.random.rand(128).tolist()
    vectors.append({
        "id": f"vec_{i}",
        "vector": vector,
        "metadata": {
            "category": f"cat_{i % 5}",
            "value": i
        }
    })

client.insert_vectors("demo_index", vectors)

# Search for similar vectors
print("\nSearching...")
query = np.random.rand(128).tolist()
results = client.search_vectors(
    index_name="demo_index",
    vector=query,
    k=5,
    filter_expr="value < 50"
)

print(f"Found {len(results.get('results', []))} results:")
for r in results.get('results', []):
    print(f"  - {r['id']}: distance={r['distance']:.4f}")

# Get index info
info = client.get_index_info("demo_index")
print(f"\nIndex info: {info}")

# Clean up
print("\nCleaning up...")
client.delete_index("demo_index")
print("Done!")
```

## Advanced Features

### Hybrid Search (Dense + Sparse Vectors)

```python
# Create index with sparse vector support
client.create_index(
    index_name="hybrid_index",
    dim=128,
    enable_sparse=True
)

# Insert vectors with sparse components
vectors = [{
    "id": "hybrid_vec1",
    "vector": [0.1] * 128,           # Dense vector
    "sparse_vector": {                # Sparse vector (token_id: weight)
        100: 0.5,
        200: 0.3,
        300: 0.8
    },
    "metadata": {"type": "hybrid"}
}]

client.insert_vectors("hybrid_index", vectors)

# Search with hybrid vectors
results = client.search_vectors(
    index_name="hybrid_index",
    vector=[0.15] * 128,
    k=5,
    sparse_vector={100: 0.6, 200: 0.4}
)
```

### Using Context Manager

```python
# Automatically close the session when done
with EndeeClient("http://localhost:8080") as client:
    indexes = client.list_indexes()
    print(indexes)
# Session is automatically closed here
```

### Error Handling

```python
from endee_client import EndeeClient, EndeeAPIError, EndeeConnectionError

client = EndeeClient("http://localhost:8080")

try:
    # Try to create an index
    client.create_index(
        index_name="test_index",
        dim=128,
        space_type="l2"
    )
except EndeeAPIError as e:
    print(f"API Error: {e}")
    print(f"Status Code: {e.status_code}")
except EndeeConnectionError as e:
    print(f"Connection Error: {e}")
```

## Configuration Options

### Client Parameters

- `base_url`: Endee server URL (default: `http://localhost:8080`)
- `auth_token`: Authentication token (optional, required if server has `NDD_AUTH_TOKEN` set)
- `timeout`: Request timeout in seconds (default: 30)

### Index Parameters

- `dim`: Vector dimensionality (required)
- `space_type`: Distance metric
  - `l2`: Euclidean distance (L2)
  - `ip`: Inner product
  - `cosine`: Cosine similarity
- `ef_construction`: HNSW build-time parameter (default: 200, higher = better quality, slower build)
- `m`: HNSW connectivity parameter (default: 16, higher = better recall, more memory)
- `quant_type`: Vector quantization
  - `none`: No quantization
  - `scalar`: Scalar quantization
  - `product`: Product quantization
- `enable_sparse`: Enable sparse vector support (default: False)

### Search Parameters

- `k`: Number of nearest neighbors to return
- `ef_search`: HNSW search-time parameter (optional, higher = better recall, slower search)
- `filter_expr`: Metadata filter expression (optional)

## Performance Tips

1. **Batch Insert**: Insert vectors in batches for better performance
2. **Tune HNSW Parameters**:
   - Increase `ef_construction` for better index quality
   - Increase `m` for better recall at the cost of memory
   - Adjust `ef_search` to balance speed and accuracy
3. **Use Quantization**: Enable quantization for large-scale datasets to reduce memory usage
4. **Filter Optimization**: Create indexes on frequently filtered metadata fields

## API Reference

For complete API documentation, see the docstrings in the `EndeeClient` class:

```python
from endee_client import EndeeClient
help(EndeeClient)
```

## Support

- **Documentation**: [docs.endee.io](https://docs.endee.io)
- **GitHub**: [github.com/mohan01052004/endee](https://github.com/mohan01052004/endee)
- **Issues**: Report bugs and request features on GitHub

## License

The Endee Python SDK is licensed under the Apache License 2.0, same as the main Endee project.
