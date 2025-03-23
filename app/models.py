from flask_login import UserMixin
from pydantic import BaseModel, RootModel

from .group_parser import validate

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
    tags: list[str] = []
    groups: str | None = None
    limit: int = 100

class TileConfigurationRequest(BaseModel):
    title: str | None = None
    tags: str | None = None
    groups: str | None = None
    limit: int = 100

    def parse(self) -> TileConfiguration:
        tags = []
        if self.tags is not None and len(self.tags) > 0:
            tags = [i for i in self.tags.split() if i]

        return TileConfiguration(
            title = self.title,
            tags = tags,
            groups = validate(self.groups) if self.groups else None,
            limit = self.limit)

class TileConfigurationList(RootModel):
    root: list[TileConfiguration]

class LinkdingBookmark(BaseModel):
    title: str
    url: str

class LinkdingResponse(BaseModel):
    results: list[LinkdingBookmark]

class TilesSettingsRequest(BaseModel):
    tiles: list[TileConfigurationRequest]
