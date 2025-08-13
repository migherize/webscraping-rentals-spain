import scrapy


class EaieItem(scrapy.Item):

    department_name = scrapy.Field()
    department_description = scrapy.Field()
    team_name = scrapy.Field()
    team_description = scrapy.Field()
    person_name = scrapy.Field()
    person_title = scrapy.Field()
    person_description = scrapy.Field()
    department_url = scrapy.Field()
    person_linked_in_url = scrapy.Field()
    person_foto = scrapy.Field()
