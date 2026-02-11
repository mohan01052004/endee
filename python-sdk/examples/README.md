# Endee Python SDK Examples

This directory contains example scripts demonstrating how to use the Endee Python SDK.

## Prerequisites

1. Install the SDK:
   ```bash
   cd python-sdk
   pip install -e .
   ```

2. Start an Endee server:
   ```bash
   # From the repository root
   ./install.sh --release --avx2
   ./run.sh
   ```

   Or using Docker:
   ```bash
   docker run -p 8080:8080 -v endee-data:/data endeeio/endee-server:latest
   ```

## Examples

### 1. basic_usage.py
Basic introduction to the SDK covering:
- Connecting to the server
- Creating an index
- Inserting vectors
- Searching for similar vectors
- Deleting an index

```bash
python examples/basic_usage.py
```

### 2. filtered_search.py
Advanced example showing:
- Metadata filtering
- Batch operations
- Complex filter expressions
- Vector deletion by filter

```bash
python examples/filtered_search.py
```

### 3. hybrid_search.py
Demonstrates hybrid search with:
- Dense vector embeddings
- Sparse vector representations
- Combined dense + sparse search

```bash
python examples/hybrid_search.py
```

### 4. authentication.py
Shows how to:
- Handle authentication
- Manage errors gracefully
- Use context managers
- Configure timeouts

```bash
python examples/authentication.py
```

## Customizing Examples

All examples connect to `http://localhost:8080` by default. To use a different server:

```python
client = EndeeClient(base_url="http://your-server:8080")
```

If your server requires authentication:

```python
client = EndeeClient(
    base_url="http://localhost:8080",
    auth_token="your_token_here"
)
```
