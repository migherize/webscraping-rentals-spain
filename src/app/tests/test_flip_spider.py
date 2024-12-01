import unittest
from scrapy.http import HtmlResponse
from app.tests.flip_spider import FlipSpider


class TestFlipSpider(unittest.TestCase):
    def setUp(self):
        self.spider = FlipSpider()

    def test_parse(self):
        html_content = """
        <html>
            <body>
                <h2 class="room-title">Room A</h2>
                <h2 class="room-title">Room B</h2>
            </body>
        </html>
        """
        response = HtmlResponse(
            url="https://flipcoliving.com/", body=html_content, encoding="utf-8"
        )
        result = self.spider.parse(response)
        expected_output = {"room_titles": ["Room A", "Room B"]}
        self.assertEqual(result, expected_output)
