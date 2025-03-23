import requests

from . import linkding
from .grouper_transformer import create_grouper
from .models import LinkTilesConfigurationExport, Tile, TileConfiguration, TileConfigurationList, TileGroup, TilesOptions
from .storage import storage

def update_tiles_configuration(user_id: str, tiles: list[TileConfiguration]) -> None:
    storage.upsert_tiles(user_id, tiles)

def get_tiles_configuration(user_id: str) -> list[TileConfiguration]:
    return storage.get_tiles(user_id) or []

def export_tiles_configuration(user_id: str) -> LinkTilesConfigurationExport:
    tiles = storage.get_tiles(user_id) or []
    return LinkTilesConfigurationExport(tiles=tiles)

def get_tiles_options(user_id: str) -> TilesOptions:
    return storage.get_tiles_options(user_id)

def update_tiles_options(user_id: str, options: TilesOptions) -> None:
    return storage.upsert_tiles_options(user_id, options)


def create_tile(user_id: str, prototype: TileConfiguration) -> Tile | str:
    user_data = storage.get_user_data(user_id)
    if user_data is None:
        return "Error retrieving account information"
    if user_data.linkding is None:
        return "No linkding API configuration found. Go to the settings panel to add it."

    tag_list = []
    if prototype.tags is not None:
        tag_list = [i for i in prototype.tags.strip().split() if i]

    try:
        linkding_response = linkding.query(
            user_data.linkding.base_url,
            user_data.linkding.api_key,
            tag_list,
            prototype.limit
        )
    except Exception as e:
        return f"Failed to query the linkding API: {e}"

    title: str | None = None
    if prototype.title is not None:
        title = prototype.title.strip()
        if len(title) == 0:
            title = None

    grouper = None
    if prototype.groups is not None:
        groups_string = prototype.groups.strip()
        if len(groups_string) > 0:
            grouper = create_grouper(groups_string)

    groups: list[TileGroup] = []
    if grouper is None:
        groups.append(TileGroup(
            title=None,
            links=[l.as_link() for l in linkding_response.results]
        ))
    if grouper is not None:
        groups = [TileGroup(title=i, links=[]) for i in grouper.get_groups()]
        orphaned_links = []
        for result in linkding_response.results:
            link = result.as_link()
            group_index = grouper.get_group_index(result.tag_names)
            if group_index is not None:
                groups[group_index].links.append(link)
            else:
                orphaned_links.append(link)
        if len(orphaned_links) > 0:
            groups.append(TileGroup(title=None, links=orphaned_links))

    return Tile(
        title=title,
        groups=groups,
        seed=prototype.seed
    )
