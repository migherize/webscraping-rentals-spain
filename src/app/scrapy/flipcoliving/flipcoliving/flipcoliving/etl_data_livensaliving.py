from app.scrapy.common import (
    extract_cost,
    parse_elements,
    extract_id_label,
    get_id_from_name,
    search_feature_with_map,
    search_location,
    get_all_imagenes,
    load_json,
    extract_area,
    decode_clean_string
)
import app.scrapy.funcs as funcs
from app.models.schemas import (
    PriceItem,
    Property,
    RentalUnits,
    LocationAddress,
    Text,
    mapping,
)
import re
from app.config.settings import GlobalConfig
from app.models.features_spider import EquivalencesLivensaLiving
from app.models.enums import PaymentCycleEnum, CurrencyCode, Pages
from app.scrapy.common import (
    create_json,
    filtrar_ids_validos,
    remove_accents,
    safe_attr,
)
from app.services.csvexport import CsvExporter

import logging
from pathlib import Path
from typing import Dict, Any

import re

def extract_area_and_clean_features(features):
    area_pattern = re.compile(r'^(\d{1,3}-\d{1,3})m²?$')
    area = None
    cleaned_features = []

    for feature in features:
        match = area_pattern.match(feature.replace(" ", ""))
        if match:
            area = match.group(1) + "m²"
        elif feature == "2":
            continue
        else:
            cleaned_features.append(feature)

    return area, cleaned_features


def clear_descripcion(descripcion):
    if not descripcion:
        return "None"

    if isinstance(descripcion, list):
        descripcion = " ".join(descripcion)

    texto = re.sub(r"\s+", " ", descripcion).strip()

    if texto == "":
        return "None"

    return texto


def format_adress(info, postal_code=""):
    street = info.get("address", "").strip().title()
    city = info.get("city", "").capitalize()
    estado = info.get("state", "").capitalize()

    return f"{street}, {postal_code} {city}, {estado}"

def get_reference_code(property_name: str) -> str:
    if not property_name:
        return ""

    if len(property_name) > 30:
        words = property_name.split()
        property_name = " ".join(words[:2])

    reference_code = remove_accents(property_name).replace(" ", "_").replace(".", "")
    return reference_code

def retrive_lodgerin_property(item, elements, address):
    data_city = item["items_output"].get("info_city", {})
    info_aux_property = item["items_output"].get("info_aux_property", {})
    data_property = item["items_output"].get("main_data_property", {})

    PropertyTypeId = get_id_from_name(
        elements["propertiesTypes"].data, "Apartment / Entire flat", "name_en"
    )
    element_feature = extract_id_label(elements["features"].data)
    area, features = extract_area_and_clean_features(data_property["feature"])
    
    features_id = search_feature_with_map(
        features,
        element_feature,
        EquivalencesLivensaLiving.FEATURES,
    )
    
    # full_address = ', '.join(data_property["address"][:3])
    # if full_address.startswith("PT,"):
    #     full_address = full_address[3:]
    # full_address = full_address.strip()
    # full_address = ' '.join(full_address.split())
    # print(f"full_address: {full_address}")
    address = search_location(address['data'][0])
    reference_code = get_reference_code(info_aux_property.get("name")[0])
    images = get_all_imagenes(data_property["images"])

    property_items = Property(
        referenceCode=reference_code,
        cancellationPolicy=GlobalConfig.CANCELLATION_POLICY,
        rentalType=GlobalConfig.RENTAL_TYPE,
        isActive=True,
        isPublished=True,
        Features=features_id,
        tourUrl=data_property.get("property_video", None),
        PropertyTypeId=PropertyTypeId,
        Texts=Text(
            description_en=None,
            description_es=clear_descripcion(
                info_aux_property["description"]
            ),
            title_en=None,
            title_es=clear_descripcion(
                info_aux_property["title"]
            ),
        ),
        Images=images,
        Location=LocationAddress(
            lat=str(safe_attr(address, "lat")),
            lon=str(safe_attr(address, "lon")),
            country=safe_attr(address, "country"),
            countryCode=safe_attr(address, "countryCode"),
            city=safe_attr(address, "city"),
            street=safe_attr(address, "street"),
            state=safe_attr(address, "state"),
            prefixPhone=safe_attr(address, "prefixPhone"),
            postalCode=safe_attr(address, "postalCode"),
            number=safe_attr(address, "number"),
            fullAddress=safe_attr(address, "fullAddress"),
            address=safe_attr(address, "address"),
        ),
        provider=Pages.livensaliving.value,
        providerRef=reference_code,
    )

    return property_items


def retrive_lodgerin_rental_units(
    data_property: Property, rental_unit: dict, elements
):
    type_and_description_rental_unit = rental_unit.get("type_and_description_rental_unit", [])
    more_information = rental_unit.get("more_information", [])
    cost_and_reservation = rental_unit.get("cost_and_reservation", [])

    element_feature = extract_id_label(elements["features"].data)
    _, features = extract_area_and_clean_features(rental_unit.get("features", ""))
    features_id = search_feature_with_map(
        features,
        element_feature,
        EquivalencesLivensaLiving.FEATURES,
    )
    rental_name_1 = rental_unit.get("name_1", "")[0].replace(" ", "_")
    rental_id = rental_name_1 +"_"+ type_and_description_rental_unit[0].replace(" ", "_")
    rental_title = rental_unit.get("name_1", "")[0] + " "+ type_and_description_rental_unit[0]
    rental_description = clear_descripcion(
        rental_unit.get("description", "")
    )
    rental_images = get_all_imagenes(rental_unit.get("images", []))
    reference_code = decode_clean_string(rental_id)
    if len(reference_code) > 30:
        reference_code = reference_code[:30]
    
    # print("rental_images", rental_images)
    # print("rental_id", rental_id)
    # print("features_id", features_id)
    # print("rental_title", rental_title)
    # print("rental_description", rental_description)
    # print("******************************")

    if len(cost_and_reservation)==3:
        cost = extract_cost(cost_and_reservation[1])
    elif len(cost_and_reservation)==4:
        cost = extract_cost(cost_and_reservation[2])

    data_rental_units = RentalUnits(
        Images=rental_images,
        PropertyId=data_property.id,
        referenceCode=reference_code,
        isActive=True,
        isPublished=True,
        areaM2=extract_area(more_information[0]),
        Price=PriceItem(
            contractType=PaymentCycleEnum.MONTHLY.value,
            currency=CurrencyCode.EUR.value,
            amount=cost,
            depositAmount=cost,
            reservationAmount=GlobalConfig.INT_ZERO,
            minPeriod=GlobalConfig.INT_ONE,
            paymentCycle=PaymentCycleEnum.MONTHLY.value,
        ),
        Texts=Text(
            description_en=None,
            description_es=clear_descripcion(rental_description),
            title_en=None,
            title_es=clear_descripcion(rental_title),
        ),
        ExtraFeatures=filtrar_ids_validos(features_id),
    )

    return data_rental_units

def process_property(
    data: Dict[str, Any], elements: Dict[str, Any], api_key: str, exporter: CsvExporter, address: Dict[str, Any] = {}
) -> None:
    """
    Procesa una propiedad y sus unidades de renta, guarda en API, exporta CSV y JSON.
    """
    print("Processing property...")

    prop_obj = retrive_lodgerin_property(data, elements, address)
    prop_id = funcs.save_property(prop_obj, api_key)
    prop_obj.id = prop_id
    create_json(prop_obj, Pages.livensaliving.value)
    logging.info("Saved property %s", prop_id)
    
    rentals = data.get("items_output", {}).get("main_data_rental", []).get("all_rental_units", [])[0]
    if rentals:
        all_types = rentals.get("all_types", [])
        for rental in all_types:
            rental["name_1"] = rentals.get("name_1", [])
            rental["name_2"] = rentals.get("name_2", [])
            rental["description"] = rentals.get("description", [])
            rental["features"] = rentals.get("features", [])
            rental["images"] = rentals.get("images", [])
            rent_obj = retrive_lodgerin_rental_units(prop_obj, rental, elements)
            rent_id = funcs.save_rental_unit(rent_obj, api_key)
            rent_obj.id = rent_id
            create_json(rent_obj, Pages.livensaliving.value)
            logging.info("Saved rental unit %s", rent_id)
            exporter.process_and_export_to_csv(prop_obj, rent_obj)
    else:
        exporter.process_and_export_to_csv(prop_obj)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )

    base_dir = Path(__file__).resolve().parent.parent
    ruta_json1 = base_dir / 'data' / 'livensaliving' / 'livensaliving.json'
    ruta_json2 = base_dir / 'data' / 'elements.json'
    ruta_json3 = base_dir / 'data' / 'livensaliving' / 'address.json'
    datos_json1 = load_json(ruta_json1)
    datos_json2 = load_json(ruta_json2)
    datos_json3 = load_json(ruta_json3)
    full_json = datos_json2.get('data', [])

    # Preparar pipeline
    elements_dict = parse_elements(full_json, mapping)
    api_key = elements_dict['api_key'].data[0].name
    exporter = CsvExporter(Pages.livensaliving.value)

    # Procesar cada elemento
    for entry, address in zip(datos_json1,datos_json3):
        if entry == datos_json1[0]:
            continue
        process_property(entry, elements_dict, api_key, exporter, address)


if __name__ == '__main__':
    main()
