import unittest

from aideas.app.agent.translation.translator import TextLines


class TextLinesTest(unittest.TestCase):
    def test_line_with_one_break(self):
        text_lines = TextLines("""Line 0.
        Line 1.

        Line 2.""")
        lines = text_lines.get_lines_without_breaks()
        self.assertEqual(3, len(lines))
        self.assertEqual(1, text_lines.get_break_count())
        self.assertEqual(4, len(text_lines.with_breaks(lines)))

    def test_line_with_multiple_breaks(self):
        text_lines = TextLines("""Line 0.
        
        Line 1.

        Line 2.""")
        lines = text_lines.get_lines_without_breaks()
        self.assertEqual(3, len(lines))
        self.assertEqual(2, text_lines.get_break_count())
        self.assertEqual(5, len(text_lines.with_breaks(lines)))

    def test_line_without_breaks(self):
        text_lines = TextLines("""Line 0.""")
        lines = text_lines.get_lines_without_breaks()
        self.assertEqual(1, len(lines))
        self.assertEqual(0, text_lines.get_break_count())
        self.assertEqual(1, len(text_lines.with_breaks(lines)))

    def test_falsy_line(self):
        self.assertRaises(ValueError, TextLines, "")


if __name__ == '__main__':
    unittest.main()
