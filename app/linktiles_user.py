from lark import UnexpectedCharacters, UnexpectedToken
from .models import LinkdingApiConnectionData, TileConfiguration, TileConfigurationRequest
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

def try_parse_tile_configurations(request: list[TileConfigurationRequest]) -> tuple[bool, list[str], list[TileConfiguration]]:
    errors = []
    configurations = []
    for i, config in enumerate(request):
        if config.groups is None:
            try:
                parsed = config.parse()
                configurations.append(parsed)
            except Exception as e:
                _logger.error(e)
                errors.append(f"tile_config_{i}: {type(e).__name__}")
            continue

        try:
            parsed = config.parse()
            configurations.append(parsed)
        except UnexpectedCharacters as e:
            errors.append(f"tile_config_{i}: Unexpected character '{e.char}' at position {e.column} in group string {config.groups}")
            continue
        except UnexpectedToken as e:
            errors.append(f"tile_config_{i}: Unexpected token '{e.token}' at position {e.column} in group string {config.groups}")
            continue
        except Exception as e:
            _logger.error(e)
            errors.append(f"tile_config_{i}: {type(e).__name__}")

    return len(errors) == 0, errors, configurations

