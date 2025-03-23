import requests

from .models import LinkdingResponse


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

def query(url: str, api_key: str, tags: list[str] = [], limit: int = 100) -> LinkdingResponse:
    base_url = url.rstrip("/")
    headers = { "Authorization": f"Token {api_key}" }
    
    params = {"limit": str(limit)}
    if tags and len(tags) > 0:
        tag_query = " ".join(tags)
        params["q"] = tag_query
    
    try:
        response = requests.get(
            f"{base_url}/api/bookmarks/", 
            headers=headers,
            params=params
        )
        response.raise_for_status()
        return LinkdingResponse.model_validate_json(response.text)

    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Failed to query linkding API: {str(e)}")
