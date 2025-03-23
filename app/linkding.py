import requests


def test(url: str, api_key: str) -> tuple[bool, str | None]:
    base_url = url.rstrip("/")
    headers = { "Authorization": f"Token {api_key}" }
    
    try:
        response = requests.get(f"{base_url}/api/user/profile/", headers=headers)
        response.raise_for_status()
        _ = response.json()
        return True, None
    except requests.exceptions.RequestException as e:
        return False, f"Failed to connect to linkding API: {str(e)}"

# def query(url: str, api_key: str, tags: List[str] = None, limit: int = 100) -> Dict[str, Any]:
#     """
#     Query the linkding API for bookmarks, optionally filtered by tags.
#     
#     Args:
#         url: The base URL of the linkding instance (e.g., "https://linkding.example.com")
#         api_key: The API key for authentication
#         tags: Optional list of tag names to filter by
#         limit: Maximum number of results to return (default: 100)
#         
#     Returns:
#         Dict containing query results from the API
#         
#     Raises:
#         requests.exceptions.RequestException: If the API request fails
#     """
#     # Strip trailing slash if present
#     base_url = url.rstrip("/")
#     
#     # Prepare headers with authorization token
#     headers = {
#         "Authorization": f"Token {api_key}"
#     }
#     
#     # Build query string
#     params = {"limit": limit}
#     
#     # Add tag filtering if provided
#     if tags and len(tags) > 0:
#         # Format the query string for tag search using the linkding search syntax
#         tag_query = " ".join([f"#{tag}" for tag in tags])
#         params["q"] = tag_query
#     
#     try:
#         # Make the API request
#         response = requests.get(
#             f"{base_url}/api/bookmarks/", 
#             headers=headers,
#             params=params
#         )
#         response.raise_for_status()
#         
#         return response.json()
#     
#     except requests.exceptions.RequestException as e:
#         # Re-raise the exception with more context
#         raise requests.exceptions.RequestException(f"Failed to query linkding API: {str(e)}")
