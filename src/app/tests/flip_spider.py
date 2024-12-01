import scrapy


class FlipSpider(scrapy.Spider):
    name = "flip"
    start_urls = ["https://flipcoliving.com/"]

    def parse(self, response):
        room_titles = response.xpath("//h2[@class='room-title']/text()").getall()
        return {"room_titles": room_titles}
