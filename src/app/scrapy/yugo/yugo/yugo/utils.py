from enum import Enum
from typing import List, Dict
from app.scrapy.common import extract_id_name, search_feature_with_map
from app.config.settings import GlobalConfig
from app.scrapy.common import (
    get_id_from_name,
    get_all_imagenes,
    decode_clean_string,
    extract_area,
    search_location
)
from app.models.enums import PaymentCycleEnum, CurrencyCode
from app.models.schemas import (
    PriceItem,
    Property,
    RentalUnits,
    RentalUnitsCalendarItem,
    LocationAddress,
    ApiKeyItem,
    Text
)
from app.models.features_spider import EquivalencesYugo

class PropertyTypeColiving(Enum):
    PROPERTY_TYPE = (
        "Pisos",
        "Casas",
        "Edificios",
    )
    OPERATION = "alquiler"

def map_property_descriptions(languages, property_descriptions: list[dict[str, str]]) -> List[Dict]:
    language_dict = {lang.code: lang for lang in languages}
    
    texts = {
        "title_en": None,
        "title_es": None,
        "description_en": None,
        "description_es": None,
    }

    for prop in property_descriptions:
        try:
            lang_code = prop.get("language").split("-")[0].upper()

            if not prop.get("language") in ("en-us", "es-es"):
                # Ignorar aquellos que no son ingles ni espanhol
                continue
            
            language = language_dict.get(lang_code)
            if language:
                title = prop.get("property_name")
                description = prop.get("residence_description")
                if lang_code == "EN":
                    texts["title_en"] = title
                    texts["description_en"] = description
                elif lang_code == "ES":
                    texts["title_es"] = title
                    texts["description_es"] = description
            else:
                print(
                    f"Advertencia: No se encontró el idioma para el código '{lang_code}' en la propiedad '{prop.get('property_name')}'."
                )
        except Exception as e:
            print(f"Error al procesar la propiedad '{prop.get('property_name')}': {e}")
    
    return {"Texts": Text(**texts)}


def get_name_by_location(data: List[ApiKeyItem], location: str) -> str:
    """
    Busca en la lista por la ubicación (location) y devuelve el valor de 'name'.

    Args:
        data (list): Lista de diccionarios con las claves 'id', 'name' y 'location'.
        location (str): La ubicación a buscar.

    Returns:
        str: El valor de 'name' correspondiente a la ubicación, o None si no se encuentra.
    """

    for item in data:
        if item.location == location:
            return item.name
    return None

def retrive_lodgerin_property(item, elements, list_api_key):
    api_key = get_name_by_location(list_api_key, item["yugo_space_name"])
    PropertyTypeId = get_id_from_name(
        elements["propertiesTypes"].data, "Apartment / Entire flat", "name_en"
    )
    descriptions = map_property_descriptions(
        elements["languages"].data,
        item["second_items_property"],
    )
    element_feature = extract_id_name(elements["features"].data)
    features_id = search_feature_with_map(
        item["all_feature"],
        element_feature,
        EquivalencesYugo.FEATURES,
    )
    address = search_location(item['address_contact_and_email'])

    # clean reference_code
    reference_code = decode_clean_string(item["url_yugo_space"])
    images = get_all_imagenes(item["all_images"])

    if item["tour_virtual"]:
        tour_url = item["tour_virtual"][0]
    else:
        tour_url = None
    property_items = Property(
        referenceCode=reference_code,
        cancellationPolicy=GlobalConfig.CANCELLATION_POLICY,
        rentalType=GlobalConfig.RENTAL_TYPE,
        isActive=True,
        isPublished=True,
        Features=features_id,
        tourUrl=tour_url,
        PropertyTypeId=PropertyTypeId,
        Texts=descriptions.get('Texts'),
        Images=images,
        Location=LocationAddress(
            lat=str(address.lat),
            lon=str(address.lon),
            country=address.country,
            countryCode=address.countryCode,
            city=address.city,
            street=address.street,
            state=address.state,
            prefixPhone=address.prefixPhone,
            postalCode=address.postalCode,
            number=address.number,
            fullAddress=address.fullAddress,
            address=address.address,
        ),
        provider="yugo",
        providerRef=reference_code,
    )

    return property_items, api_key


def retrive_lodgerin_rental_units(
    items_property: Property, elements_dict: dict, data_scrapy: list
):
    rental_units = []
    calendar_unit_list = []

    for index, data in enumerate(data_scrapy, start=1):
        if not data.get("api_data_rental_unit", {}).get("error", []):
            start_date = safe_get(data, ("api_data_rental_unit", "tenancy-options", 0, "tenancyOption", 0, "startDate"))
            end_date = safe_get(data, ("api_data_rental_unit", "tenancy-options", 0, "tenancyOption", 0, "endDate"))
            date_text = safe_get(data, ("api_data_rental_unit", "tenancy-options", 0, "tenancyOption", 0, "formattedLabel"))
            fromYear = safe_get(data, ("api_data_rental_unit", "tenancy-options", 0, "fromYear"))
            toYear = safe_get(data, ("api_data_rental_unit", "tenancy-options", 0, "toYear"))

            """
            # amenities = data.get("api_data_rental_unit", []).get("residence", []).get("amenities", [])
            # amenities_extras = data.get("api_data_rental_unit", []).get("residence", []).get("amenitiesExternalReference", [])
            # name = data.get("api_data_rental_unit", []).get("room", []).get("name", [])
            """

            amount = safe_get(data, ("api_data_rental_unit", "room", "minPriceForBillingCycle"))
            if amount == "None":
                amount = 1

        else:
            start_date = "None"
            end_date = "None"
            amount = 1
            date_text = "None"
            fromYear = "None"
            toYear = "None"

        description_unit = data.get("response_data_rental_units", {}).get("DESCRIPTION_RENTAL_UNIT", [])
        description_text = description_unit[0] if description_unit else ""

        area = extract_area(description_text)
        area_m2 = int(area) if area is not None else None

        picture = data.get("response_data_rental_units", {}).get("picture", [])
        images = get_all_imagenes(picture) if picture else None

        data_rental_unit = RentalUnits(
            PropertyId=items_property.id,
            referenceCode=f"{items_property.referenceCode}-{index:03}",
            areaM2=area_m2,
            isActive=True,
            isPublished=True,
            Price=PriceItem(
                contractType=PaymentCycleEnum.MONTHLY.value,
                currency=CurrencyCode.EUR.value,
                amount=amount,
                depositAmount=amount,
                reservationAmount=GlobalConfig.INT_ZERO,
                minPeriod=GlobalConfig.INT_ONE,
                paymentCycle=PaymentCycleEnum.MONTHLY.value
            ),
            Features=items_property.Features,
            Texts=items_property.Texts,
            Images=images
        )
        rental_units.append(data_rental_unit)
        date_items = RentalUnitsCalendarItem(
            summary=f"Blocked until {fromYear} - {toYear}",
            description=date_text,
            startDate=start_date,
            endDate=end_date,
        )
        calendar_unit_list.append(date_items)

    return rental_units, calendar_unit_list


def safe_get(data: dict, path: tuple[str | int], default="None"):
    """
    Acceso seguro a datos anidados.
    
    :param data: Diccionario o lista inicial
    :param path: Lista de claves/índices (ej: ["user", "address", 0, "street"])
    :param default: Valor a devolver si no existe la ruta
    :return: Valor encontrado o default
    """
    current = data

    if not current:
        return default

    for key in path:
        try:
            if isinstance(current, dict):
                current = current.get(key, default)
            elif isinstance(current, list) and isinstance(key, int):
                current = current[key] if 0 <= key < len(current) else default
            else:
                return default
        except Exception:
            return default
    return current