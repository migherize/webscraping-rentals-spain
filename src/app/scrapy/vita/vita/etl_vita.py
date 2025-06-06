import re
import json
import stat
from scrapy import Spider
from typing import List, Tuple, Dict

from logging import Logger

from app.models.enums import (
    CurrencyCode, 
    Languages,
    Pages,
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
    create_json,
    search_feature_with_map,
    extract_id_label,
    filtrar_ids_validos
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

from app.models.features_spider import EquivalencesVitaStudents
from app.services.csvexport import CsvExporter

def etl_data_vita(items: List[Dict], json_elements: Dict, logger: Logger) -> None:

    elements_dict = parse_elements(json_elements, mapping)
    api_key = elements_dict["api_key"].data[0].name
    
    exporter = CsvExporter(Pages.vita.value)

    for index, item in enumerate(items):

        items_output = item['items_output']
        data_property, tours_rental_units = retrive_property(items_output)
        
        element_feature = extract_id_label(elements_dict["features"].data)
        features_id = search_feature_with_map(
            data_property["property_features"],
            element_feature,
            EquivalencesVitaStudents.FEATURES,
        )

        property_vita = Property(
            referenceCode=re.sub(r'\s','_', data_property['property_referend_code']),
            rentalType=GlobalConfig.RENTAL_TYPE,
            isActive=GlobalConfig.BOOL_TRUE,
            isPublished=GlobalConfig.BOOL_TRUE,
            Features=features_id,
            tourUrl=tours_rental_units,
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
        property_vita.id = property_id
        create_json(property_vita, Pages.vita.value)

        logger.info("Property ID: %s", property_id)
        list_rental_unit_id = []

        for index_rental_unit, rental_unit in enumerate(items_output['all_rental_units']):
            try:

                data_rental_units, calendar_unit_list = retrive_rental_unit(rental_unit, property_vita, element_feature)

                # RentalUnit
                rental_unit_id = save_rental_unit(data_rental_units, api_key)
                data_rental_units.id = rental_unit_id
                list_rental_unit_id.append(data_rental_units)
                create_json(data_rental_units, Pages.vita.value)
                

                # schedule
                for rental_id, calendar_unit in zip(
                    list_rental_unit_id, calendar_unit_list
                ):
                    if calendar_unit.startDate == "None":
                        continue
                    check_and_insert_rental_unit_calendar(
                        rental_id.id, calendar_unit, api_key
                    )

                for calendar_unit in calendar_unit_list:
                    create_json(calendar_unit, Pages.vita.value)

                exporter.process_and_export_to_csv(property_vita, data_rental_units)
                
            except Exception as error:
                logger.warning(error)


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
        "property_tours_360": items_output['property_tours_360'],                        # list
        "property_cost": items_output['property_cost'],                                  # str
        "property_referend_code": (
            f"{items_output['property_name'][0]}_{items_output['property_city']}"
        )
    }

    if data_property_vita['property_tours_360'] and len(data_property_vita['property_tours_360']) > 1:
        data_property_vita['property_tours_360'] = items_output['property_tours_360'][0]
    else:
        data_property_vita['property_tours_360'] = None
    tours_rental_units = data_property_vita['property_tours_360']
    if tours_rental_units == '':
        tours_rental_units = None

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
    raw = property_data.get("property_cost", "")
    raw = raw.split(r'\u')[0]
    clean = raw.strip('"')
    if clean:
        num = re.sub(r'\.', '', clean).replace(',', '.')
        try:
            property_data["property_cost"] = float(num)
        except ValueError:
            property_data["property_cost"] = ''
    else:
        property_data["property_cost"] = ''

    return None


def retrive_rental_unit(rental_unit:Dict[str, str | List | Dict], property_data: Property, element_feature) -> None:

    rental_unit_room_data = rental_unit.get("rental_unit_room_data",[])[0]
    rental_unit_booking_data = rental_unit.get("rental_unit_booking_data",{})
    calendar_unit_list = []

    features_id = search_feature_with_map(
        rental_unit_room_data.get("standard_features"),
        element_feature,
        EquivalencesVitaStudents.FEATURES,
    )

    try:
        rental_unit = RentalUnits(
            PropertyId=property_data.id,
            referenceCode=rental_unit.get("rental_unit_room_code"),
            areaM2=rental_unit_room_data.get("size").replace("sqm", ""),
            isActive=True,
            isPublished=True,
            Texts=property_data.Texts,
            Images=get_all_imagenes(rental_unit_room_data.get("images")),
            Price=PriceItem(
                contractType=PaymentCycleEnum.MONTHLY.value,
                currency=rental_unit_room_data.get("currency"),
                amount=int(extract_cost(rental_unit.get("rental_unit_cost"))),
                depositAmount=int(extract_cost(rental_unit.get("rental_unit_cost"))),
                reservationAmount=GlobalConfig.INT_ZERO,
                minPeriod=GlobalConfig.INT_ONE,
                paymentCycle=PaymentCycleEnum.MONTHLY.value
            ),
            ExtraFeatures=filtrar_ids_validos(features_id),
        )
        
        start_date = rental_unit_booking_data.get("terms",[])[0].get("startDate")
        end_date = rental_unit_booking_data.get("terms",[])[0].get("endDate")
        description = rental_unit_booking_data.get("terms",[])[0].get("name")

        date_items = RentalUnitsCalendarItem(
            summary=f"Blocked until {start_date} - {end_date}",
            description=description,
            startDate=start_date,
            endDate=end_date,
        )
        calendar_unit_list.append(date_items)

        return rental_unit, calendar_unit_list
    except Exception as e:

        return rental_unit, calendar_unit_list
        # pprint(type(e), e)
        # pprint(rental_unit)
        # pprint(tours_rental_units)
