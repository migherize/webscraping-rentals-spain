from enum import Enum


class ConfigPages(Enum):
    BASE_URL = 'https://www.livensaliving.com/'
    ITEMS_COUNTRIES = {
        'spain': 'https://www.livensaliving.com/residencias-estudiantes-espana/',
        # 'portugal': 'https://www.livensaliving.com/residencias-estudiantes-portugal/',
    }
    PATH_RENTAL_UNITS = 'habitaciones-y-precios/'
    PATH_FEATURE_PROPERTY = 'servicios-residencia/'
    PATH_GENERAL_IMAGES = 'galeria-residencia/'


class ConfigCity(Enum):
    PIVOTE = "//h2[@class='subrayado']"
    TITLE = "./a/text()"
    URL = "./a/@href"
    DESCRIPTION = "./../../../div[3]//text()"


class ConfigProperty(Enum):
    PIVOTE = "//h2[@class='subrayado']"
    NAME = "./text()"
    TITLE = "./../h3/text()"
    DESCRIPTION = "./../../../div[2]//text()"
    URL = "./../../../div[3]//@href"

    # menuresidencia

    DESCRIPTION_1 = "//div[contains(@id, 'menu')]/div/div[1]//text()"
    PHONE = "//a[contains(@id, 'res_cen_tel')]/@href"
    MAIL = "//a[contains(@id, 'res_mail')]/@href"
    ADDRESS = "//div[contains(@id, 'menu')]//ul/li[last()]//text()"
    DESCRIPTION_2 = "//div[contains(@class, 'subrayado')]/..//text()"
    # DESCRIPTION_3 = "//div[contains(@class, 'et_pb_row_4')][1]//text()"
    GALLERY = "//div[contains(@class, 'gallery_image')]//@href"
