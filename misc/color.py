import math
from typing import Any


class Color:
    def __init__(self, r: int, g: int, b: int ) -> None:
        if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
            raise Exception("Color values must be between 0 and 255")
        self.r = r
        self.g = g
        self.b = b

    def __sub__(self, other: Any) -> Color:
        return Color(
            max(self.r - other.r, 0),
            max(self.g - other.g, 0),
            max(self.b - other.b, 0))

    def __add__(self, other: Any) -> Color:
        if isinstance(other, Color):
            return Color(
                min(self.r + other.r, 255),
                min(self.g + other.g, 255),
                min(self.b + other.b, 255))
        if isinstance(other, tuple) and len(other) == 3:
            return Color(
                min(self.r + other[0], 255),
                min(self.g + other[1], 255),
                min(self.b + other[2], 255))
        return NotImplemented

    def __eq__(self, other):
        return self.r == other.r and self.g == other.g and self.b == other.b

    @staticmethod
    def interval(color_start: Color, color_end: Color) -> tuple[int, int, int]:
        return (
            color_end.r - color_start.r,
            color_end.g - color_start.g,
            color_end.b - color_start.b)

    def to_kml_hex(self) -> str:
        return f'ff{self.b:02x}{self.g:02x}{self.r:02x}'

    def to_hex(self) -> str:
        return f'#{self.r:02x}{self.g:02x}{self.b:02x}'


class ColorInterpolation:
    def __init__(self, color_start: Color, color_end: Color, val_min: float, val_max: float) -> None:
        self.color_start = color_start
        self.color_end = color_end
        self.val_min = val_min
        self.val_max = val_max

    def _factor(self, val: float) -> float:
        if val < self.val_min or val > self.val_max:
            raise Exception(f"Value must be between {self.val_min} and {self.val_max}")
        return (val - self.val_min) / (self.val_max - self.val_min)

    def interpolate(self, val: float) -> Color:
        factor = self._factor(val)
        color_diff = (
            round((self.color_end.r - self.color_start.r) * factor),
            round((self.color_end.g - self.color_start.g) * factor),
            round((self.color_end.b - self.color_start.b) * factor)
        )
        return self.color_start + color_diff