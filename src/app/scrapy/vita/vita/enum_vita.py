from enum import Enum


class ConfigXpath(Enum):
    ALL_URL_PROPERTY = "//a[contains(@class, 'view-building')]/@href"
    BASIC_DATA_PROPERTY = {
        'property_name': "//h1/text()",
        'property_address': "//div[contains(@class, 'address')]/text()",
        'property_description_en': "//div[contains(@class, '__excerpt')]//text()",
        'property_feature': "//div[contains(@class, 'features__row')]//li//text()",
        'property_plans': "//a[contains(@href, '.pdf')]/@href",
        'property_images': "(//div[contains(@class, 'glide__slides')])[1]//img/@src",
        'property_tours_360': "//a[contains(@href, '/show/')]/@href"
    }
    TYPE_RENTAL_UNITS = "//div[@class='room-types-app']/@data-type"
    ALL_URL_RENTAL_UNITS = "//div[contains(@class, 'wp-block-button')]//@href"


class ConfigPropertyRequests(Enum):
    PROPERTY_URL = 'https://www.vitastudent.com/wp-json/student-accommodation/v1/development'
    PROPERTY_PAYLOAD = {
            'availability': 'true',
            # 'development': developmentid,     # Este parametro se agrega en la funcion
            "year": "2025 / 26",
            "lang": "es",
            "_locale": "user"            
        }
    PROPERTY_HEADERS = {
            "accept": "application/json, */*;q=0.1",
            "accept-language": "es-419,es;q=0.9,en-US;q=0.8,en;q=0.7",
            "cookie": "cookieyes-consent=consentid:NUVJdUNZSXNxeFlQTEwxRWlwUTgzd3dvZWZmZTJnaXg,consent:yes,action:yes,necessary:yes,functional:yes,analytics:yes,performance:yes,advertisement:yes,other:yes; _gcl_au=1.1.1681232971.1737074892; _ga=GA1.1.1091692651.1737074864; _scid=PFDWHVi8cpixtdt5jV5u9zplkpnWpVhL; _tt_enable_cookie=1; _ttp=UFWnD6hnU8__EvgFuosO3OpDrPL.tt.1; _fbp=fb.1.1737074906085.394986535714041988; pll_language=es; _ScCbts=[]; _sctr=1|1737864000000; _uetsid=12ca5510dc3b11ef9434793d09db0ced|v4vu0|2|fsx|0|1852; _scid_r=T9DWHVi8cpixtdt5jV5u9zplkpnWpVhLSEZ7Tw; _uetvid=a89305b0d46c11efb8a7098fb78301a3|4l5uns|1737943876155|5|1|bat.bing.com/p/insights/c/u; _ga_RSV8LEC89Z=GS1.1.1737933175.3.1.1737944130.60.0.1499288122",
            "priority": "u=1, i",
            "referer": "https://www.vitastudent.com/es/ciudades/barcelona/poblenou/",
            "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }


class ConfigAllRentalUnitsRequests(Enum):
    ALL_RENTAL_UNITS_URL = 'https://www.vitastudent.com/wp-json/student-accommodation/v1/rooms'
    ALL_RENTAL_UNITS_PAYLOAD = {
        # "development": developmentid,     # Este parametro se agrega en la funcion
        # "type": type_rental_unit,         # Este parametro se agrega en la funcion
        "year": "2025 / 26",
        "availability": "true",
        "lang": "en",
        "_locale": "user"
    }
    ALL_RENTAL_UNITS_HEADERS = {
        "sec-ch-ua-platform": "\"Windows\"",
        "Referer": "https://www.vitastudent.com/en/cities/barcelona/poblenou/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "application/json, */*;q=0.1",
        "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0"
    }
    
    
class ConfigRentalUnitRequests(Enum):
    RENTAL_UNIT_URL = "https://www.vitastudent.com/wp-json/student-accommodation/v1/room"
    RENTAL_UNIT_PAYLOAD = {
            # "code": room_code,        # Este parametro se agrega en la funcion
            "year": "2025 / 26",
            "availability": "false",
            "lang": "en",
            "_locale": "user"
        }
    RENTAL_UNIT_HEADERS = {
            "sec-ch-ua-platform": "\"Windows\"",
            # "Referer": f"https://www.vitastudent.com/en/cities/barcelona/poblenou/view-room-{room_code}/?academicYear=2025 / 26",     # Este parametro se agrega en la funcion
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "application/json, */*;q=0.1",
            "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0"
        }

    PLUS_DATA_RENTAL_UNIT_URL = "https://www.vitastudent.com/wp-json/student-accommodation/v1/booking"
    PLUS_DATA_RENTAL_UNIT_PAYLOAD = {
            # "code": room_code,        # Este parametro se agrega en la funcion
            "year": "2025 / 26",
            "lang": "en",
            "_locale": "user"
        }
    PLUS_DATA_RENTAL_UNIT_HEADERS = {
            "sec-ch-ua-platform": "\"Windows\"",
            # "Referer": f"https://www.vitastudent.com/en/cities/barcelona/poblenou/view-room-{room_code}/?academicYear=2025 / 26",     # Este parametro se agrega en la funcion
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "application/json, */*;q=0.1",
            "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0"
        }
    
