from .models import LinkdingApiConnectionData
from .storage import storage
import logging

def get_linkding_connection_data(user_id: str) -> LinkdingApiConnectionData | None:
    user_data = storage.get_user_data(user_id)
    return user_data.linkding if user_data is not None else None

def get_glance_token(user_id: str) -> str:
     return storage.get_glance_token_from_user_id(user_id) \
         or storage.rotate_user_glance_token(user_id)

def rotate_glance_token(user_id: str) -> str:
    return storage.rotate_user_glance_token(user_id)

def upsert_linkding_connection_data(user_id: str, base_url: str, api_key: str) -> bool:
    result = storage.get_user_and_data(user_id)
    if result is None:
        return False
    user, user_data = result
    user_data.linkding = LinkdingApiConnectionData(base_url=base_url, api_key=api_key)
    return storage.update_user(user, user_data)

