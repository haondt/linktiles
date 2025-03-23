from .models import TileConfiguration, TilesOptions
from .storage import storage

def update_tiles_configuration(user_id: str, tiles: list[TileConfiguration]) -> None:
    storage.upsert_tiles(user_id, tiles)

def get_tiles_configuration(user_id: str) -> list[TileConfiguration]:
    return storage.get_tiles(user_id) or []

def get_tiles_options(user_id: str) -> TilesOptions:
    return storage.get_tiles_options(user_id)

def update_tiles_options(user_id: str, options: TilesOptions) -> None:
    return storage.upsert_tiles_options(user_id, options)

