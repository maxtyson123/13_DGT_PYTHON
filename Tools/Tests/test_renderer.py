from unittest import TestCase

from Maxs_Modules.renderer import auto_style_text, Colour


class TestRenderer(TestCase):
    def test_auto_style_text_colour(self):
        result = auto_style_text("red", True)
        self.assertEqual(result, Colour.RED + "red" + Colour.RESET)

    def test_auto_style_text_word(self):
        result = auto_style_text("correct", True)
        self.assertEqual(result, Colour.GREEN + "correct" + Colour.RESET)
