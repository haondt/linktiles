from flask_login import confirm_login
from .models import ExtendedThinUser, LinkdingOptions, LinkdingResponse, ThinUser, TileConfiguration, TileConfigurationList, TilesOptions, User, UserData
import redis, time
from .configuration import configuration

def convert_username_to_id(username: str) -> str:
    return username.strip().upper()

class MemoryStorage():
    def __init__(self):
        self.users: dict[str, User] = {}
        self.user_data: dict[str, UserData] = {}
        self.tiles: dict[str, list[TileConfiguration]] = {}
        self.tiles_options: dict[str, TilesOptions] = {}
        self.linkding_options: dict[str, LinkdingOptions] = {}
        self.linkding_responses: dict[str, tuple[float, LinkdingResponse]] = {}

    def get_user(self, username) -> User | None:
        id = convert_username_to_id(username)
        return self.users.get(id)

    def add_user(self, username, password_hash: bytes | None) -> bool:
        id = convert_username_to_id(username)
        if self.get_user(id):
            return False
        self.users[id] = User(id)
        self.user_data[id] = UserData(username=username, password_hash=password_hash)
        return True

    def update_user(self, user: User, user_data: UserData) -> bool:
        if not self.get_user(user.id):
            return False
        self.users[user.id] = user
        self.user_data[user.id] = user_data
        return True

    def get_or_create_user(self, username) -> User | None:
        id = convert_username_to_id(username)
        self.add_user(username, None)
        return self.users[id]
    
    def get_user_data(self, username) -> UserData | None:
        id = convert_username_to_id(username)
        return self.user_data.get(id)

    def get_user_and_data(self, username) -> tuple[User, UserData] | None:
        id = convert_username_to_id(username)
        user = self.users.get(id)
        if user is None:
            return None
        data = self.user_data.get(id)
        if data is None:
            return None
        return user, data

    def upsert_tiles(self, user_id: str, tiles: list[TileConfiguration]) -> None:
        self.tiles[user_id] = tiles

    def get_tiles(self, user_id: str) -> list[TileConfiguration] | None:
        return self.tiles.get(user_id, None)

    def upsert_tiles_options(self, user_id: str, tiles_options: TilesOptions) -> None:
        self.tiles_options[user_id] = tiles_options

    def get_tiles_options(self, user_id: str) -> TilesOptions:
        result = self.tiles_options.get(user_id)
        if result:
            return result
        return TilesOptions()

    def upsert_linkding_options(self, user_id: str, linkding_options: LinkdingOptions) -> None:
        self.linkding_options[user_id] = linkding_options

    def get_linkding_options(self, user_id: str) -> LinkdingOptions:
        result = self.linkding_options.get(user_id)
        if result:
            return result
        return LinkdingOptions()

    def upsert_linkding_response(self, cache_key: str, time_to_live_seconds: int,  linkding_response: LinkdingResponse) -> None:
        self.linkding_responses[cache_key] = (time.time() + time_to_live_seconds, linkding_response)

    def get_linkding_response(self, cache_key: str) -> LinkdingResponse | None:
        hit = self.linkding_responses.get(cache_key)
        if hit is None:
            return None
        if time.time() > hit[0]:
            try:
                del self.linkding_responses[cache_key]
            except:
                pass
            return None
        return hit[1]

class RedisStorage():
    def __init__(self):
        assert configuration.db_port is not None
        self.client = redis.StrictRedis(
            host=configuration.db_host,
            port=configuration.db_port,
            password=configuration.db_password,
            charset='utf-8',
            decode_responses=True)
        self.user_prefix = 'user'
        self.tiles_prefix = 'tiles:tiles'
        self.tiles_options_prefix = 'tiles:options'
        self.linkding_options_prefix = 'linkding:options'
        self.linkding_responses_prefix = 'linkding:responses'

    def deserialize_user(self, id: str, data: str) -> tuple[User, UserData]:
        user =  ExtendedThinUser.model_validate_json(data)
        return User(id), user.data

    def serialize_user(self, user: User, user_data: UserData) -> str:
        return ExtendedThinUser(user=ThinUser(), data=user_data).model_dump_json()

    def get_user_and_data(self, username) -> tuple[User, UserData] | None:
        id = convert_username_to_id(username)
        serialized = self.client.get(f'{self.user_prefix}:{id}')
        return self.deserialize_user(id, str(serialized)) if serialized else None

    def get_user(self, username) -> User | None:
        result = self.get_user_and_data(username)
        return result[0] if result else None

    def add_user(self, username, password_hash: bytes | None) -> bool:
        id = convert_username_to_id(username)
        user = User(id)
        user_data = UserData(username=username, password_hash=password_hash)
        result = self.client.setnx(f'{self.user_prefix}:{id}', self.serialize_user(user, user_data))
        return bool(result)

    def update_user(self, user: User, user_data: UserData) -> bool:
        result = self.client.set(f'{self.user_prefix}:{user.id}', self.serialize_user(user, user_data), xx=True)
        return bool(result)

    def get_or_create_user(self, username) -> User | None:
        self.add_user(username, None)
        return self.get_user(username)
    
    def get_user_data(self, username: str) -> UserData | None:
        result = self.get_user_and_data(username)
        return result[1] if result else None

    def upsert_tiles(self, user_id: str, tiles: list[TileConfiguration]) -> None:
        assert self.client.set(f'{self.tiles_prefix}:{user_id}', TileConfigurationList(root=tiles).model_dump_json())

    def get_tiles(self, user_id: str) -> list[TileConfiguration] | None:
        result = self.client.get(f'{self.tiles_prefix}:{user_id}')
        return TileConfigurationList.model_validate_json(str(result)).root if result else None

    def upsert_tiles_options(self, user_id: str, tiles_options: TilesOptions) -> None:
        assert self.client.set(f'{self.tiles_options_prefix}:{user_id}', tiles_options.model_dump_json())

    def get_tiles_options(self, user_id: str) -> TilesOptions:
        result = self.client.get(f'{self.tiles_options_prefix}:{user_id}')
        return TilesOptions.model_validate_json(str(result)) if result else TilesOptions()

    def upsert_linkding_options(self, user_id: str, linkding_options: LinkdingOptions) -> None:
        assert self.client.set(f'{self.linkding_options_prefix}:{user_id}', linkding_options.model_dump_json())

    def get_linkding_options(self, user_id: str) -> LinkdingOptions:
        result = self.client.get(f'{self.linkding_options_prefix}:{user_id}')
        return LinkdingOptions.model_validate_json(str(result)) if result else LinkdingOptions()

    def upsert_linkding_response(self, cache_key: str, time_to_live_seconds: int,  linkding_response: LinkdingResponse) -> None:
        assert self.client.set(f'{self.linkding_responses_prefix}:{cache_key}', linkding_response.model_dump_json(), ex=time_to_live_seconds)

    def get_linkding_response(self, cache_key: str) -> LinkdingResponse | None:
        result = self.client.get(f'{self.linkding_responses_prefix}:{cache_key}')
        return LinkdingResponse.model_validate_json(str(result)) if result else None


if configuration.db_engine == 'redis':
    storage = RedisStorage()
else:
    storage = MemoryStorage()

