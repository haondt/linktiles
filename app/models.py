from flask_login import UserMixin
from lark import UnexpectedCharacters, UnexpectedToken
from pydantic import BaseModel, RootModel, field_validator

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
    tags: str | None = None
    groups: str | None = None
    limit: int = 100

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, value):
        return " ".join(value.split()) if value else None

    @field_validator("groups")
    @classmethod
    def validate_groups(cls, value):
        if value is None:
            return None
        try:
            return validate(value)
        except UnexpectedCharacters as e:
            raise ValueError(f"Unexpected character '{e.char}' at position {e.column}") from e
        except UnexpectedToken as e:
            raise ValueError(f"Unexpected token '{e.token}' at position {e.column}") from e

class TileConfigurationList(RootModel):
    root: list[TileConfiguration]

class LinkdingBookmark(BaseModel):
    title: str
    url: str

class LinkdingResponse(BaseModel):
    results: list[LinkdingBookmark]

class TilesSettingsRequest(BaseModel):
    tiles: list[TileConfiguration]

