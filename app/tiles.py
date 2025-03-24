import hashlib

from . import linkding
from .grouper_transformer import create_grouper
from .models import LinkTilesConfigurationExport, LinkdingApiConnectionData, LinkdingOptions, LinkdingResponse, Tile, TileConfiguration, TileConfigurationList, TileGroup, TilesOptions, TimeUnit, UserData
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

def get_linkding_options(user_id: str) -> LinkdingOptions:
    return storage.get_linkding_options(user_id)

def update_linkding_options(user_id: str, options: LinkdingOptions) -> None:
    return storage.upsert_linkding_options(user_id, options)


def _get_linkding_response(user_id: str, connection_data: LinkdingApiConnectionData, prototype: TileConfiguration) -> LinkdingResponse | str:
    linkding_options = storage.get_linkding_options(user_id)
    if linkding_options.cache_enabled:
        cache_key = hashlib.sha256(f"{connection_data.base_url}{connection_data.api_key}{prototype.tags}{prototype.limit}".encode()).hexdigest()
        cached = storage.get_linkding_response(cache_key)
        if cached:
            return cached

    tag_list = []
    if prototype.tags is not None:
        tag_list = [i for i in prototype.tags.strip().split() if i]

    try:
        linkding_response = linkding.query(
            connection_data.base_url,
            connection_data.api_key,
            tag_list,
            prototype.limit
        )
    except Exception as e:
        return f"Failed to query the linkding API: {e}"

    if linkding_options.cache_enabled:
        cache_key = hashlib.sha256(f"{connection_data.base_url}{connection_data.api_key}{prototype.tags}{prototype.limit}".encode()).hexdigest()
        match linkding_options.cache_duration_unit:
            case TimeUnit.MINUTES:
                ttl_seconds = linkding_options.cache_duration * 60
            case TimeUnit.HOURS:
                ttl_seconds = linkding_options.cache_duration * 60 * 60
            case TimeUnit.DAYS:
                ttl_seconds = linkding_options.cache_duration * 60 * 60 * 24
        storage.upsert_linkding_response(cache_key, int(ttl_seconds), linkding_response)

    return linkding_response

def create_tile(user_id: str, prototype: TileConfiguration) -> Tile | str:
    user_data = storage.get_user_data(user_id)
    if user_data is None:
        return "Error retrieving account information"
    if user_data.linkding is None:
        return "No linkding API configuration found. Go to the settings panel to add it."

    linkding_response = _get_linkding_response(user_id, user_data.linkding, prototype)

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
