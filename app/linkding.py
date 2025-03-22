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

