from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id):
        self.id = id

class UserData:
    def __init__(self,
                 id: str,
                 username: str, 
                 password_hash: bytes | None = None,
                 linkding_api_key: str | None = None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.linkding_api_key = linkding_api_key

