from flask_login import UserMixin
from pydantic import BaseModel, RootModel

class User(UserMixin):
    def __init__(self, id):
        self.id = id

class ThinUser(BaseModel):
    pass

class LinkdingApiConnectionData(BaseModel):
    base_url: str
    api_key: str

class UserData(BaseModel):
    username: str
    password_hash: bytes | None = None
    linkding: LinkdingApiConnectionData | None = None

class ExtendedThinUser(BaseModel):
    user: ThinUser
    data: UserData

class TileConfiguration(BaseModel):
    title: str | None = None
    tags: str | None = None
    groups: str | None = None
    limit: int = 100

class TileConfigurationList(RootModel):
    root: list[TileConfiguration]

class LinkdingBookmark(BaseModel):
    title: str
    url: str

class LinkdingResponse(BaseModel):
    results: list[LinkdingBookmark]

class TilesSettingsRequest(BaseModel):
    tiles: list[TileConfiguration]
