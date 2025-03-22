from flask import json
from flask_login import confirm_login
from .models import User, UserData
import redis, base64
from .configuration import configuration

def convert_username_to_id(username: str) -> str:
    return username.strip().upper()

class MemoryStorage():
    def __init__(self):
        self.users: dict[str, User] = {}
        self.user_data: dict[str, UserData] = {}

    def get_user(self, username) -> User | None:
        id = convert_username_to_id(username)
        return self.users.get(id)

    def add_user(self, username, password_hash: bytes | None) -> bool:
        id = convert_username_to_id(username)
        if self.get_user(id):
            return False
        self.users[id] = User(id)
        self.user_data[id] = UserData(id, username, password_hash)
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

class RedisStorage():
    def __init__(self):
        assert configuration.db_port is not None
        self.client = redis.Redis(
            host=configuration.db_host,
            port=configuration.db_port,
            password=configuration.db_password,
            decode_responses=True)
        self.user_prefix = 'user'

    def deserialize_user(self, id: str, data: str) -> tuple[User, UserData]:
        j = json.loads(data)
        user = j['user']
        user_data = j['data']
        password_hash_string = user_data.get('password_hash')
        if password_hash_string is None:
            password_hash = None
        else:
            password_hash = base64.b64decode(password_hash_string)

        linkding_api_key = user_data.get('linkding_api_key')

        return User(id), UserData(id, user_data['username'], password_hash, linkding_api_key)

    def serialize_user(self, user: User, user_data: UserData):
        if user_data.password_hash is None:
            password_hash_string = None
        else:
            password_hash_string = base64.b64encode(user_data.password_hash).decode('utf-8')

        j = {
            'user': {},
            'data': {
                'username': user_data.username,
                'password_hash': password_hash_string,
                'linkding_api_key': user_data.linkding_api_key
            }
        }

        return json.dumps(j)

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
        user_data = UserData(id, username, password_hash)
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

if configuration.db_engine == 'redis':
    storage = RedisStorage()
else:
    storage = MemoryStorage()

