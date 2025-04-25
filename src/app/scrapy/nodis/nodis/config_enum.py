from enum import Enum


class ConfigPages(Enum):
    BASE_URL = "https://nodis.es/en/home-nodis-student-residences/"
    # URL_PROPERTY = "(//div[contains(@class, 'container p-0')])[1]//a/@href"
    URL_PROPERTY = "//a[contains(@title, 'The Residences')]/../ul/li/a/@href"
    
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
        # "|"
        # '//div[contains(@data-widget_type, "heading.default")]//p/text()'
    )
    
    DESCRIPTION_2 = (
        "(//div[@class='p-5'])[1]//text()"
        # "|"
        # ""
    )

    URL_RENTAL_UNIT = "//a[contains(@href, '.greenlts')]/@href"
    

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



"""
class AllXpath(Enum):

    ALL_URL_PROPERTY = "(//div[contains(@class, 'container p-0')])[1]//a/@href"
    DATA_PROPERTY_ENGLISH = {
        'property_info_1': "//div[contains(@class, 'marginNeg')]//h2//text()",
        'property_info_2': "(//div[@class='p-5'])[1]//text()",
    }
    URL_SPANISH = "//a[@lang='es-ES']/@href" 
    DATA_PROPERTY_SPANISH = {
        # 'property_name': '//button[@id="dropdownMenuButton"]/../../../p[1]//text()',
        'property_name': '//button[@id="dropdownMenuButton"]/../../../p[1]//text()|//span[@class="elementor-button-text"]/text()',
        'property_info_1': "//div[contains(@class, 'marginNeg')]//h2//text()",
        'property_info_2': "(//div[@class='p-5'])[1]//text()",
        'property_features': "//figure//text()",
        'property_features_info': "(//div[@class='p-5'])[2]//text()",
    }
"""