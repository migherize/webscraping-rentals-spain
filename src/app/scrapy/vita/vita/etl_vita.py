import re
import json
from scrapy import Spider
from typing import List, Tuple, Dict

from app.models.enums import (
    CurrencyCode, 
    Languages,
    PaymentCycleEnum, 
    feature_map,
)
from app.models.schemas import (
    PriceItem,
    Property,
    RentalUnits,
    RentalUnitsCalendarItem,
    LocationAddress,
    ApiKeyItem,
    Text,
    mapping
)

from app.scrapy.common import (
    parse_elements,
    get_all_imagenes,
    search_location,
    extract_area,
    extract_cost,
    create_json
)
from app.scrapy.funcs import (
    check_and_insert_rental_unit_calendar,
    detect_language,
    find_feature_keys,
    get_elements_types,
    get_month_dates,
    save_property,
    save_rental_unit,
)

from app.config.settings import GlobalConfig

from pprint import pprint


def etl_data_vita(items: List[Dict], spider: Spider) -> None:

    elements_dict = parse_elements(spider.context, mapping)
    api_key = elements_dict["api_key"].data[0].name

    for index, item in enumerate(items):

        items_output = item['items_output']
        data_property, tours_rental_units = retrive_property(items_output)

        property_vita = Property(
            referenceCode=data_property['property_referend_code'],
            rentalType=GlobalConfig.RENTAL_TYPE,
            isActive=GlobalConfig.BOOL_TRUE,
            isPublished=GlobalConfig.BOOL_TRUE,
            Features=find_feature_keys(data_property['property_features'], feature_map), # TODO: Mapear
            tourUrl=data_property["property_tours_360"],
            PropertyTypeId=get_elements_types(GlobalConfig.PROPERTY_TYPE_ID, elements_dict["propertiesTypes"]),
            Texts=Text(
                description_en=data_property['property_description_en'][0],
                description_es=data_property['property_description_es'][0],
                title_en=data_property['property_name'],
                title_es=data_property['property_name'],
            ),
            Images=data_property['property_images'],
            Location=LocationAddress(
                lat=str(data_property["property_address"].lat),
                lon=str(data_property["property_address"].lon),
                country=data_property["property_address"].country,
                countryCode=data_property["property_address"].countryCode,
                city=data_property["property_address"].city,
                street=data_property["property_address"].street,
                state=data_property["property_address"].state,
                prefixPhone=data_property["property_address"].prefixPhone,
                postalCode=data_property["property_address"].postalCode,
                number=data_property["property_address"].number,
                fullAddress=data_property["property_address"].fullAddress,
                address=data_property["property_address"].address,
            )
        )
        property_id = save_property(property_vita, api_key)
        create_json(property_vita)

        # if not items_output['all_rental_units']:
        #     continue

        # for index_rental_unit, rental_unit in enumerate(items_output['all_rental_units']):
        #     retrive_rental_unit(
        #         index_rental_unit, rental_unit, tours_rental_units[index_rental_unit]
        #     )
        #     break
        # break


def retrive_property(items_output: Dict[str, str | List]) -> Tuple[Dict[str, str | List], List]:
    data_property_vita: Dict[str, str | List] = {
        "property_city": items_output['property_city'],                                  # str
        "property_name": items_output['property_name'][0],                               # str
        "property_address": items_output['property_address'][0],                         # str
        "property_description_en": items_output['property_description_en'],              # list
        "property_description_es": items_output['property_description_es'],              # list
        "property_features": items_output['property_feature'],                           # list
        "property_plans": items_output['property_plans'],                                # list
        "property_images": items_output['property_images'],                              # list
        "property_tours_360": items_output['property_tours_360'].pop(0),                 # list
        "property_cost": items_output['property_cost'],                                  # str
        "property_referend_code": (
            f"{items_output['property_name'][0]}_{items_output['property_city']}"
        )
    }
    tours_rental_units = items_output['property_tours_360']
    clean_data_property(data_property_vita)
    return data_property_vita, tours_rental_units


def clean_data_property(property_data: Dict[str, str | List]) -> None:

    # Por los momentos, no se acomodan
    property_data["property_city"]
    property_data["property_name"]
    property_data["property_tours_360"]
    property_data["property_description_en"]
    property_data["property_description_es"]
    property_data["property_referend_code"]
    
    # Obtener la dirección
    property_data["property_address"] = search_location(
        property_data["property_address"].replace('Vita Student', '').strip()
    )

    # Obtener los feature
    property_data["property_features"] = list(map(
        lambda feature: feature.replace('–', '-'), property_data["property_features"]
    ))
    
    # Agregar los planos a las imagenes
    for plan in property_data["property_plans"]:
        property_data["property_images"].append(plan)

    # Obtener formato de las imagenes
    property_data["property_images"] = get_all_imagenes(property_data["property_images"])

    # Obtener Cost
    property_data["property_cost"] = property_data["property_cost"].split('\\u')[0]
    property_data["property_cost"] = (
        float(re.sub(r'[."]', '', property_data["property_cost"]).replace(',', '.'))
        if property_data["property_cost"] else ''
    )

    return None


def retrive_rental_unit(index_rental_unit: int, rental_unit:Dict[str, str | List | Dict]):
    pprint(rental_unit)
    data_rental_vita: Dict[str, str | List] = {
        "rental_referend_code": '',
        "rental_cost": '',
        "rental_room_type": '',
        "rental_": '',
        "rental_": '',
    }
