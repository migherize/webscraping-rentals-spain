# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TheDistrictShowItem(scrapy.Item):
    name_speaker = scrapy.Field()
    image_speaker = scrapy.Field()
    linkedin_speaker = scrapy.Field()
    whatsapp_speaker = scrapy.Field()
    X_speaker = scrapy.Field()
    company = scrapy.Field()
    company_position_speaker = scrapy.Field()
    description_speaker = scrapy.Field()
    name_session = scrapy.Field()
    date_session = scrapy.Field()
    address = scrapy.Field()
    source_speaker_url = scrapy.Field()