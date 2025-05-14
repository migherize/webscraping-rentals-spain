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



GENERAL_HEADERS={
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "es-ES,es;q=0.9",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}
GENERAL_COOKIES={
    "PHPSESSID": "77lf741b6nqpgnkcqn1141rk93",
    "_ga": "GA1.1.1578515642.1747228025",
    "_gcl_au": "1.1.732995370.1747228025",
    "_ga_02JMGME37V": "GS2.1.s1747228024$o1$g0$t1747228024$j0$l0$h1146083975",
    "_fbp": "fb.1.1747228026220.1882728717811351",
    "_wpfuuid": "2796b3bb-663d-426c-8b07-47c60200fc36",
    "__insp_wid": "681480779",
    "__insp_slim": "1747228026551",
    "__insp_nv": "true",
    "__insp_targlpu": "aHR0cHM6Ly9mbGlwY29saXZpbmcuY29tLw==",
    "__insp_targlpt": "Q29saXZpbmcgaW4gc3BhaW4uIEZsaXBjbyEgeW91ciBob21lIGluIHRoZSBjZW50cmUgb2YgTWFkcmlkIGFuZCBNw6FsYWdh",
    "__insp_norec_sess": "true",
    "cmplz_consented_services": "",
    "cmplz_policy_id": "16",
    "cmplz_marketing": "allow",
    "cmplz_statistics": "allow",
    "cmplz_preferences": "allow",
    "cmplz_functional": "allow",
    "cmplz_banner-status": "dismissed",
    "pys_session_limit": "true",
    "pys_start_session": "true",
    "pys_first_visit": "true",
    "pysTrafficSource": "direct",
    "pys_landing_page": "https://flipcoliving.com/",
    "last_pysTrafficSource": "direct",
    "last_pys_landing_page": "https://flipcoliving.com/",
    "pbid": "1cfeb233356bc5c9a40ffb7acaeec1662bdb184e35f1fa16e162a2e9a0cca903"
}
