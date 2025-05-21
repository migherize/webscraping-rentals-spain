from enum import Enum


class ConfigPages(Enum):
    BASE_URL = 'https://www.livensaliving.com/'
    ITEMS_COUNTRIES = {
        'spain': 'https://www.livensaliving.com/residencias-estudiantes-espana/',
        'portugal': 'https://www.livensaliving.com/residencias-estudiantes-portugal/',
    }
    PATH_RENTAL_UNITS = "//a[contains(.//text(), 'Habitaciones y Precios')]/@href"
    PATH_FEATURE_PROPERTY = 'servicios-residencia/'
    PATH_GENERAL_IMAGES = 'galeria-residencia/'


class ConfigCity(Enum):
    PIVOTE = "//h2[@class='subrayado']"
    TITLE = "./a/text()"
    URL = "./a/@href"
    DESCRIPTION = "./../../../div[3]//text()"


class ConfigProperty(Enum):

    # -------------------------------------------------------------------
    # Busqueda de la propiedad en la ciudad
    PIVOTE = "//h2[@class='subrayado']"
    NAME = "./text()"
    TITLE = "./../h3/text()"
    DESCRIPTION = "./../../../div[2]//text()"
    URL = "./../../../div[3]//@href"

    # -------------------------------------------------------------------
    # Pagina de la propiedad
    DESCRIPTION_1 = "//div[contains(@id, 'menu')]/div/div[1]//text()"
    PHONE = "//a[contains(@id, 'res_cen_tel')]/@href"
    MAIL = "//a[contains(@id, 'res_mail')]/@href"
    ADDRESS = "//div[contains(@id, 'menu')]//ul/li[last()]//text()"
    DESCRIPTION_2 = (
        "//div[contains(@class, 'subrayado')]/..//text()"
        "|"
        "//h3[contains(@class, 'subrayado')]/../../..//text()"
        "|"
        "//div[contains(@class, 'et_pb_text_3 ')]/..//text()"
    )
    # DESCRIPTION_3 = "//div[contains(@class, 'et_pb_row_4')][1]//text()"
    GALLERY = "//div[contains(@class, 'gallery_image')]//@href"

    # -------------------------------------------------------------------
    # Pagina de los feature
    FEATURE = "//div[contains(@class, 'servicios_disponibles_col')]//text()"


class ConfigRentalUnits(Enum):
    PIVOTE = "//h3[contains(text(), 'incluye')]/.."
    NAME_1 = "./h2[1]/text()"
    NAME_2 = "./h3[1]/text()"
    DESCRIPTION = "./p[1]/text()"
    FEATURES = "./div//text()|./p[2]/text()|./p[contains(text(), '|')]/text()"

    PIVOTE_IMAGES = "//h3[contains(text(), 'incluye')]/../../../../div[2]"
    IMAGES = ".//div[contains(@class, 'dipi-image-gallery-top')]//div[contains(@href, '.jpg')]/@href"

    PIVOTE_TYPE_RENTAL = "//div[re:test(@id, '^mostrar\\d+$')]"
    TYPE_AND_DESCRIPTION_RENTAL_UNIT = "./div[1]//div[contains(@class, 'hds')]//text()"
    MORE_INFORMATION = "./div[1]//div[contains(@class, 'hdi')]//text()"
    COST_AND_RESERVATION = "./div[2]/div[1]//text()"