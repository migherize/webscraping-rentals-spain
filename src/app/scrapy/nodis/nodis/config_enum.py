from enum import Enum


class ConfigPages(Enum):
    BASE_URL = "https://nodis.es/"
    HEADERS = {
        "Referer": "https://nodis.es/en/home-nodis-student-residences/",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }
    URL_PROPERTY = (
        "//a[contains(@title, 'The Residences')]/../ul/li/a/@href"
        "|"
        "//a[contains(@title, 'Las Residencias')]/../ul/li/a/@href"
    )
    
    CONTACT = (
        "//span[contains(text(), 'Contact us')]"
        "|"
        "//a[contains(text(), 'Contact us')]"
    )

class ConfigXpathProperty(Enum):
    
    NAME = "//title//text()"
    IMAGES = "//img[contains(@src, '.jpg')]/@src"
    VIDEO = "//video/@src"
    FEATURES = (
        "//figcaption[@class='wp-element-caption']/text()"
        "|"
        "//div[@class='elementor-gallery-item__title']/text()"
    )
    PHONE = (
        "//div[contains(text(), 'Phone')]/../../../div//text()"
        "|"
        "//p[contains(text(), 'Telephone') or contains(text(), 'Phone')]//text()"
    )


    DESCRIPTION_1 = (
        "//div[contains(@class, 'marginNeg')]//h2//text()"
        "|"
        '//div[contains(@data-id, "02b45f9")]//text()'
        "|"
        '//div[contains(@data-id, "14e88e6")]//text()'
    )
    
    DESCRIPTION_2 = (
        "(//div[@class='p-5'])[1]//text()"
        "|"
        '//div[contains(@data-id, "3e04ed3")]//text()'
    )

    # URL_RENTAL_UNIT = "//a[contains(@href, '.greenlts')]/@href"
    URL_RENTAL_UNIT = (
        "//div[contains(@data-id, 'bd7254a')]//@href"
        "|"
        "//a[contains(text(), 'Reserva ya')]/@href"
        # "|"
        # "//a[contains(text(), 'Contáctanos')]/@href"
    )

    URL_RENTAL_UNIT_NEW_PAGE = "//a[contains(@href, 'greenlts')]/@href"
    AUX_ADDRESS_PROPERTY = '//div[@data-id="83b3789"]//p//text()'
    

class CityNameImages(Enum):
    SEARCH_IMAGES: dict[str, str] = {
        'Vicalvaro': r'/Vicalvaro',
        'Granada': r'/Granada',
        'Barcelona': r'/Barcelona',
        'Pozuelo': r'_Pozuelo_',
        'Girona': r'/Girona|/Barcelona_Girona',
        'Zaragoza': r'/Zaragoza|-zaragoza-|_Zaragoza_',
        'Malaga': r'/Malaga|Estudiantes_Malaga',
        'Sevilla': r'/Sevilla|_Sevilla_',
    }
