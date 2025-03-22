from flask_login import UserMixin
from pydantic import BaseModel, RootModel

class User(UserMixin):
    def __init__(self, id):
        self.id = id

class ThinUser(BaseModel):
    pass

class UserData(BaseModel):
    username: str
    password_hash: bytes | None = None
    linkding_api_key: str | None = None
    class Config:
        exclude_none = True

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
