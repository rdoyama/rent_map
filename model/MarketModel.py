from pydantic import ConfigDict
from pydantic.dataclasses import dataclass


@dataclass(config=ConfigDict(extra='ignore'))
class MarketModel:
    name: str
    lat: float
    lon: float

    icon_color: str = None
    icon_scale: float = 1.3

    label_scale: float = 0.7

