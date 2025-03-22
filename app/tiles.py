from .models import TileConfiguration
from .storage import storage

def update_tiles_configuration(user_id: str, tiles: list[TileConfiguration]) -> None:
    storage.upsert_tiles(user_id, tiles)

def get_tiles_configuration(user_id: str) -> list[TileConfiguration]:
    return storage.get_tiles(user_id) or []

