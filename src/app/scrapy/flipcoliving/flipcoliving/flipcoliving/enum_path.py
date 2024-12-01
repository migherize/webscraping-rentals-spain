from enum import Enum


class XpathGeneralColiving(Enum):

    LANGUAGE_URL = "//div[contains(@class, 'languageDropdown')]//a/@href"

    CITIES_URL = '//ul[contains(@id, "menu-locations-menu-1")]//@href'
    COLIVING_URL = "//a[contains(@class, 'card__textBottom')]//@href"
    FIRST_IMAGENES = (
        "//div[contains(@class, 'carouselBanner__imageWrap')]//img/@src|"
        "//div[contains(@class, 'carouselBanner__imageWrap')]//img/@data-flickity-lazyload-src|"
        "//div[contains(@class, 'carouselBanner__imageWrap')]//img/@srcset|"
        "//div[contains(@class, 'floorPlan__imageWrap')]//@data-src"
    )
    COLIVING_NAME = "//h2[contains(@class, 'carouselBanner__title')]/text()"
    BANNER_FEATURES = (
        "//ul[contains(@class, 'carouselBanner__features')]/li/p/text()|"
        "//ul[contains(@class, 'carouselBanner__features')]//span[contains(text(), 'From')]/text()"
    )
    ABOUT_THE_HOME = "//div[contains(@class, 'sectionIntro__text')]//p/text()"
    FEATURES = "//span[contains(@class, 'homesFeatures__text')]/text()"
    TYPE_NAME_RENTAL_UNIT = "//h2[@class='theRooms__title']//text()"
    TOUR_URL = "//iframe[contains(@src, 'matterport')]/@src"
    LATITUDE = "//div[contains(@class, 'localAreaMap__half')]//@data-lng"
    LONGITUDE = "//div[contains(@class, 'localAreaMap__half')]//@data-lat"

    # xpath de unicos rental unit
    NAME_RENTAL_UNIT = "//div[contains(@class, 'card--available')]//h3[contains(@class, 'card__title')]/text()"
    AVAILABLE_RENTAL_UNIT = "//span[contains(@class, 'card__label')]/text()"
    DATA_RENTAL_UNIT = "//div[contains(@class, 'card--available')]//div[contains(@class, 'card__textWrap')]//span/text()"
    IMAGENES_RENTAL_UNIT = "//div[contains(@class, 'card__top')]//div[contains(@class, 'card__imageFrame')]//img/@data-srcset"

    # xpath multiples rental unit
    MULTIPLE_NAME_RENTAL_UNIT = ".//h3[contains(@class, 'card__title')]//text()"
    MULTIPLE_AVAILABLE_RENTAL_UNIT = ".//span[contains(@class, 'card__label')]//text()"
    MULTIPLE_DATA_RENTAL_UNIT = (
        ".//div[contains(@class, 'card__features')]//span//text()"
    )
    MULTIPLE_IMAGENES_RENTAL_UNIT = ".//img/@data-srcset"
