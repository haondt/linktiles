from lark import UnexpectedCharacters, UnexpectedToken
from .models import LinkdingApiConnectionData, TileConfiguration
from .storage import storage
import logging

_logger = logging.getLogger(__name__)

def get_linkding_connection_data(user_id: str) -> LinkdingApiConnectionData | None:
    user_data = storage.get_user_data(user_id)
    return user_data.linkding if user_data is not None else None

def upsert_linkding_connection_data(user_id: str, base_url: str, api_key: str) -> bool:
    result = storage.get_user_and_data(user_id)
    if result is None:
        return False
    user, user_data = result
    user_data.linkding = LinkdingApiConnectionData(base_url=base_url, api_key=api_key)
    return storage.update_user(user, user_data)

