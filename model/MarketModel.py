from pydantic import ConfigDict
from pydantic.dataclasses import dataclass


@dataclass(config=ConfigDict(extra='ignore'))
class MarketModel:
    name: str
    lat: float
    lon: float

    #icon: str = 'http://maps.google.com/mapfiles/kml/pal3/icon18.png'
    icon: str = 'resources/grocery_icon.png'
    icon_color: str = None
    icon_scale: float = 0.9

    label_scale: float = 0.7

