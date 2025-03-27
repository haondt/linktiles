import asyncio
import hashlib
import aiohttp
import json

from . import linkding
from .grouper_transformer import create_grouper
from .models import BookmarkSortOrder, LinkTilesConfigurationExport, LinkdingApiConnectionData, LinkdingBookmark, LinkdingOptions, LinkdingResponse, Tile, TileConfiguration, TileConfigurationList, TileGroup, TilesOptions, TimeUnit, UserData
from .storage import storage

def update_tiles_configuration(user_id: str, tiles: list[TileConfiguration]) -> None:
    storage.upsert_tiles(user_id, tiles)

def get_tiles_configuration(user_id: str) -> list[TileConfiguration]:
    return storage.get_tiles(user_id) or []

def create_tile(user_id: str, prototype: TileConfiguration, tiles_options: TilesOptions) -> Tile | str:
    user_data = storage.get_user_data(user_id)
    if user_data is None:
        return "Error retrieving account information"
    if user_data.linkding is None:
        return "No linkding API configuration found. Go to the settings panel to add it."

    linkding_response = _get_linkding_response(user_id, user_data.linkding, prototype)
    if isinstance(linkding_response, str):
        return linkding_response

    return create_tile_from_linkding_response(prototype, linkding_response, tiles_options)

async def create_tiles_async(user_id: str) -> list[Tile] | str:
    user_data = storage.get_user_data(user_id)
    linkding_options = storage.get_linkding_options(user_id)
    tiles_options = storage.get_tiles_options(user_id)
    if user_data is None:
        return "Error retrieving account information"
    if user_data.linkding is None:
        return "No linkding API configuration found. Go to the settings panel to add it."

    prototypes = storage.get_tiles(user_id) or []

    async with aiohttp.ClientSession() as session:
        tasks = [_get_linkding_response_async(linkding_options, user_data.linkding, p, session) for p in prototypes]
        results = await asyncio.gather(*tasks)

    errors = [i for i in results if isinstance(i, str)]
    if len(errors) > 0:
        return '\n'.join(errors)

    tiles = []
    for i in range(len(prototypes)):
        linkding_response = results[i]
        assert isinstance(linkding_response, LinkdingResponse) # make the linter happy
        tile = create_tile_from_linkding_response(prototypes[i], linkding_response, tiles_options)
        tiles.append(tile)
    return tiles

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

def _compute_cache_key(connection_data: LinkdingApiConnectionData, prototype: TileConfiguration, ttl_seconds: int) -> str:
    key_data = {
        "base_url": connection_data.base_url,
        "api_key": connection_data.api_key,
        "tags": prototype.tags,
        "limit": prototype.limit,
        "duration": ttl_seconds # poor mans cache invalidation
    }
    key_string = json.dumps(key_data, sort_keys=True)
    return hashlib.sha256(key_string.encode()).hexdigest()

def _compute_cache_time_to_live(linkding_options: LinkdingOptions) -> int:
    match linkding_options.cache_duration_unit:
        case TimeUnit.MINUTES:
            return int(linkding_options.cache_duration * 60)
        case TimeUnit.HOURS:
            return int(linkding_options.cache_duration * 60 * 60)
        case TimeUnit.DAYS:
            return int(linkding_options.cache_duration * 60 * 60 * 24)

async def _get_linkding_response_async(linkding_options: LinkdingOptions, connection_data: LinkdingApiConnectionData, prototype: TileConfiguration, session: aiohttp.ClientSession) -> LinkdingResponse | str:
    ttl_seconds = None
    cache_key = None
    if linkding_options.cache_enabled:
        ttl_seconds = _compute_cache_time_to_live(linkding_options)
        cache_key = _compute_cache_key(connection_data, prototype, ttl_seconds)
        cached = storage.get_linkding_response(cache_key)
        if cached:
            return cached

    tag_list = []
    if prototype.tags is not None:
        tag_list = [i for i in prototype.tags.strip().split() if i]

    try:
        linkding_response = await linkding.query_async(
            connection_data.base_url,
            connection_data.api_key,
            tag_list,
            prototype.limit,
            session
        )
    except Exception as e:
        return f"Failed to query the linkding API: {e}"

    if linkding_options.cache_enabled:
        ttl_seconds = ttl_seconds or _compute_cache_time_to_live(linkding_options)
        cache_key = cache_key or _compute_cache_key(connection_data, prototype, ttl_seconds)
        storage.upsert_linkding_response(cache_key, int(ttl_seconds), linkding_response)

    return linkding_response

def _get_linkding_response(user_id: str, connection_data: LinkdingApiConnectionData, prototype: TileConfiguration) -> LinkdingResponse | str:
    linkding_options = storage.get_linkding_options(user_id)
    ttl_seconds = None
    cache_key = None
    if linkding_options.cache_enabled:
        ttl_seconds = _compute_cache_time_to_live(linkding_options)
        cache_key = _compute_cache_key(connection_data, prototype, ttl_seconds)
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
        ttl_seconds = ttl_seconds or _compute_cache_time_to_live(linkding_options)
        cache_key = cache_key or _compute_cache_key(connection_data, prototype, ttl_seconds)
        storage.upsert_linkding_response(cache_key, ttl_seconds, linkding_response)

    return linkding_response



def create_tile_from_linkding_response(prototype: TileConfiguration, linkding_response: LinkdingResponse, tiles_options: TilesOptions) -> Tile | str:
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
    match tiles_options.bookmark_sort_order:
        case BookmarkSortOrder.DEFAULT:
            pass
        case BookmarkSortOrder.ALPHABETICAL:
            for group in groups:
                group.links = sorted(group.links, key=lambda l: l.name)
        case BookmarkSortOrder.ADDED:
            for group in groups:
                group.links = sorted(group.links, key=lambda l: l.date_added, reverse=True)
        case BookmarkSortOrder.FIRST_ADDED:
            for group in groups:
                group.links = sorted(group.links, key=lambda l: l.date_added)
        case BookmarkSortOrder.MODIFIED:
            for group in groups:
                group.links = sorted(group.links, key=lambda l: l.date_modified, reverse=True)

    return Tile(
        title=title,
        groups=groups,
        seed=prototype.seed
    )
