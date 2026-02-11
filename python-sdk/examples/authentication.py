"""
Example showing how to use authentication and handle errors.
"""

from endee_client import EndeeClient, EndeeAPIError, EndeeConnectionError

def main():
    # Example 1: Connection without authentication
    print("1. Connecting without authentication...")
    try:
        client = EndeeClient(base_url="http://localhost:8080")
        health = client.health_check()
        print(f"   Success: {health}")
    except EndeeConnectionError as e:
        print(f"   Connection failed: {e}")
    except EndeeAPIError as e:
        print(f"   API error: {e} (Status: {e.status_code})")
    
    # Example 2: Connection with authentication
    print("\n2. Connecting with authentication...")
    try:
        # If your server has NDD_AUTH_TOKEN set, provide it here
        auth_token = "your_auth_token_here"  # Replace with actual token
        client = EndeeClient(
            base_url="http://localhost:8080",
            auth_token=auth_token
        )
        health = client.health_check()
        print(f"   Success: {health}")
    except EndeeAPIError as e:
        print(f"   Authentication error: {e}")
        if e.status_code == 401:
            print("   Hint: Check your auth token")
    
    # Example 3: Handling API errors
    print("\n3. Handling API errors...")
    client = EndeeClient(base_url="http://localhost:8080")
    
    try:
        # Try to create an index with invalid parameters
        client.create_index(
            index_name="test",
            dim=-1,  # Invalid dimension
            space_type="invalid"  # Invalid space type
        )
    except EndeeAPIError as e:
        print(f"   Expected error: {e}")
        print(f"   Status code: {e.status_code}")
    
    # Example 4: Handling missing index
    print("\n4. Handling missing index...")
    try:
        client.get_index_info("nonexistent_index")
    except EndeeAPIError as e:
        print(f"   Expected error: {e}")
    
    # Example 5: Using context manager for automatic cleanup
    print("\n5. Using context manager...")
    with EndeeClient("http://localhost:8080") as client:
        try:
            stats = client.get_stats()
            print(f"   Server stats retrieved successfully")
        except Exception as e:
            print(f"   Error: {e}")
    print("   Session automatically closed")
    
    # Example 6: Custom timeout
    print("\n6. Using custom timeout...")
    client = EndeeClient(
        base_url="http://localhost:8080",
        timeout=5  # 5 second timeout
    )
    try:
        health = client.health_check()
        print(f"   Success with 5s timeout: {health}")
    except EndeeConnectionError as e:
        print(f"   Timeout error: {e}")

if __name__ == "__main__":
    main()
