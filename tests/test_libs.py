"""Unit tests for the bundled markdown2 / html2text libraries."""

import os
import sys
import unittest

LIB = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib")
if LIB not in sys.path:
    sys.path.insert(0, LIB)

import markdown2  # noqa: E402
import html2text  # noqa: E402


class TestMarkdown2(unittest.TestCase):

    def test_bold_and_code(self):
        self.assertEqual(
            markdown2.markdown("**bold** and `code`"),
            "<p><strong>bold</strong> and <code>code</code></p>\n")

    def test_heading(self):
        self.assertIn("<h1>Title</h1>", markdown2.markdown("# Title"))

    def test_list(self):
        html = markdown2.markdown("- item1\n- item2")
        self.assertIn("<ul>", html)
        self.assertIn("<li>item1</li>", html)
        self.assertIn("<li>item2</li>", html)


class TestHtml2Text(unittest.TestCase):

    def setUp(self):
        self.h2t = html2text.HTML2Text()
        self.h2t.body_width = 0

    def test_heading_and_bold(self):
        self.assertEqual(
            self.h2t.handle("<h1>Title</h1><p>hello <b>world</b></p>"),
            "# Title\n\nhello **world**\n")

    def test_link(self):
        self.assertIn(
            "[example](http://example.com)",
            self.h2t.handle('<a href="http://example.com">example</a>'))


if __name__ == "__main__":
    unittest.main()
