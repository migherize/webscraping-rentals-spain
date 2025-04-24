from enum import Enum


class ConfigXpath(Enum):
    ARTICLE_DATA = "//article[contains(a/@href, '/spain/')]"
    ARTICLE_DATA_VIEW_ROOMS = "//div[contains(@class, 'product__details')]"

    ITEMS_CITY_DATA = {
        'city_name': './/h4//text()',
        'description_city': './/p//text()',
        'url_city': './/a//@href',
    }

    ITEMS_YUGO_SPACE_DATA = {
        'yugo_space_name': './h3/a/text()',
        'description_yugo_space': './/p//text()',
        'url_yugo_space': './/a//@href',
    }

    ITEMS_PROPERTY = {
        "city_name": "//h5[contains(@class, 'residence__city')]/text()",
        "property_name": "//h1[contains(@class, 'residence__title')]/text()",
        "residence_description": "//div[contains(@class, 'residence__description')]/p//text()",
    }

    ITEMS_PROPERTY_GENERAL = {
        # "address_contact_and_email": "//div[@class='residence__contact-details']//p//text()|//div[@class='address-desc']//p//text()",
        "student_rooms": "//a[contains(text(), 'View all rooms')]/@href",
        'tour_virtual': "//a[contains(@href, 'noupunt.com')]/@href",
    }

    ITEMS_PICTURE = "//section[contains(@class, 'media__container')]"

    ITEMS_FEATURE = {
        'all_feature': "//article[contains(@class, 'icon-logo')]/h6/text()|//div[@class='amenities-desc']/text()"
    }

    ITEMS_LANGUAGES = "//ul[@id='weglot-listbox']//@href"

    ALL_LINK_RENTAL_UNITS = "//h4[contains(@class, 'product-tile')]/../@href"

    # -----------------------------------------------------------------
    # Rental units

    ITEMS_RENTAL_UNITS = {
        "PROPERTY_AND_CITY": "//div[@class='sticky']/h4/text()",
        "NAME_RENTAL_UNIT": "//div[@class='sticky']/h3/text()",
        "COST": "//div[@class='sticky']/h6/text()",
        "DESCRIPTION_RENTAL_UNIT": "//div[contains(@class, 'product__description')]//p//text()",
        "ALL_INCLUSIVE": "//div[contains(@class, 'product__description')]//ul//text()",
        "ROOM_FEATURE": "//h2[contains(text(), 'Room features')]/..//article//text()",
        "SOCIAL_SPACES": "//h2[contains(text(), 'included')]/..//article//h6/text()|//h2[contains(text(), 'Social Space')]/..//article//text()",
        "STATUS": "//div[@id='cm-placement-product-details']//p[contains(text(), 'SOLD OUT')]/text()",
    }

    ITEMS_PICTURE_RENTAL_UNITS = "//picture[contains(@class, 'gallery-carousel__item--modal')]"


class ConfigXpathOtherCountries(Enum):
    ARTICLE_DATA_VIEW_ROOMS = '//article[contains(@class, "comparison-carousel__item")]'

    ITEMS_YUGO_SPACE_DATA = {
        'city_name': './/h5//text()',
        'yugo_space_name': './/h4//text()',
        'description_yugo_space': './/p//text()',
        'url_yugo_space': './/a//@href',
    }

    VERIFY_MORE_PASS = (
        "//a[contains(text(), 'Find out more')]"
        "|"
        "//a[contains(text(), 'Explore Space')]"
        "|"
        "//a[contains(text(), 'Explore space')]"
        "|"
        "//a[contains(text(), 'Discover')]"
    )