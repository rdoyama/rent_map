import unittest
from misc.color import Color, ColorInterpolation

class TestColors(unittest.TestCase):

    def test_color_creation(self):
        with self.assertRaises(Exception):
            _ = Color(-1, 0, 128)
        with self.assertRaises(Exception):
            _ = Color(1, 267, 128)
        with self.assertRaises(Exception):
            _ = Color(6, 122, -10)

    def test_color_operators(self):
        color1 = Color(1, 1, 1)
        color2 = Color(2, 2, 2)
        color3 = Color(255, 255, 255)

        self.assertEqual(color1 + color2, Color(3, 3, 3))
        self.assertEqual(color1 - color3, Color(0, 0, 0))
        self.assertEqual(color2 + color3, Color(255, 255, 255))

    def test_hex(self):
        color = Color(66, 245, 102)
        self.assertEqual(color.to_hex(), "#42f566")
        color = Color(245, 66, 215)
        self.assertEqual(color.to_hex(), "#f542d7")

    def test_color_interpolation(self):
        color1 = Color(255, 255, 255)
        color2 = Color(200, 8, 255)
        val1 = 0
        val2 = 100
        ci = ColorInterpolation(color1, color2, val1, val2)
        self.assertEqual(ci.interpolate(50).to_hex(), "#e383ff")


if __name__ == '__main__':
    unittest.main()