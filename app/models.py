from enum import Enum
import random
from flask_login import UserMixin
from lark import UnexpectedCharacters, UnexpectedToken
from pydantic import BaseModel, Field, RootModel, field_validator

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
    seed: float = Field(default_factory=lambda: random.uniform(0, 1))
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


class TileColors(str, Enum):
    RANDOM = "Random"
    REALLY_RANDOM = "Really random"
    DARK = "Dark"
    DARKER = "Darker"
    BRIGHTER = "Brighter"
    BRIGHT = "Bright"

class TileFill(str, Enum):
    FILL = "Fill"
    OUTLINE = "Outline"

class TileTitleLocation(str, Enum):
    INSIDE = "Inside"
    OUTSIDE = "Outside"

class TileLayout(str, Enum):
    MASONRY = "Masonry"
    GRID = "Grid"
    LIST = "List"

class TileGroupLayout(str, Enum):
    DEFAULT = "Default"
    LOOSE = "Loose"
    LIST = "List"

class TilesOptions(BaseModel):
    colors: TileColors = TileColors.RANDOM
    fill: TileFill = TileFill.FILL
    title_location: TileTitleLocation = TileTitleLocation.OUTSIDE
    layout: TileLayout = TileLayout.MASONRY
    width: int = 300
    group_layout: TileGroupLayout = TileGroupLayout.DEFAULT
