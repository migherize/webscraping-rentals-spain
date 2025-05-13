import json
from scrapy import Spider
from logging import Logger
from pathlib import Path
from typing import Dict, Any

from app.scrapy.nodis.nodis.spiders.nodis_spider import clean_data
from app.scrapy.common import (
    read_json,
    parse_elements,
    extract_id_label,
    get_id_from_name,
    search_feature_with_map,
    search_location,
    get_all_imagenes,
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
from app.models.features_spider import EquivalencesNodis
from app.models.enums import PaymentCycleEnum, CurrencyCode, Pages
from app.scrapy.common import (
    create_json,
    filtrar_ids_validos,
    remove_accents,
    safe_attr,
)
from app.services.csvexport import CsvExporter


def etl_data_nodis(output_path: str, spider: Spider, logger: Logger):
    
    items: list[dict[str, str]] = read_json(output_path)
    if items == []:
        logger.warning('- No existe informacion en el archivo JSON para refinar')
        return None
    
    extractor_data_etl = ExtractorData(items, logger)
    output_data_nodis = list(extractor_data_etl.extractor_main_info())

    # TODO: Realzar el proceso de guardar la informacion para Lodgerin con la "output_data_nodis"
    
    # Preparar pipeline
    elements_dict = parse_elements(spider.context, mapping)
    api_key = elements_dict['api_key'].data[0].name
    exporter = CsvExporter(Pages.nodis.value)

    # Procesar cada elemento
    for entry in output_data_nodis:
        process_property(entry, elements_dict, api_key, exporter)

class ExtractorData:
    
    def __init__(self, items, logger):
        self.items: list[str, dict] = items
        self.logger: Logger = logger
    
    def extractor_main_info(self):

        # ------------------------------------------------------------------------------------------
        # Recorrer los items extraidos de nodis

        for index_data_property, data_nodies in enumerate(self.items):
            data_property = data_nodies.get('items_output', {}).get('property', {})

            # --------------------------------------------------------------------------------------
            # Si existe informacion de la propiedad 

            if data_property in ({}, None):
                self.logger.warning(
                    'En la posicion numero "%s" de la data json no contiene propiedad. Cheqeuar', 
                    index_data_property
                )
                continue

            self.logger.info('Refinando la propiedad: "%s"', data_property['property_name'])

            # --------------------------------------------------------------------------------------
            # Extraer la informacion de la propiedad

            output_data_property: dict = self.extractor_data_property(data_property)
            output_data_property: Property = self.create_output_property_model(output_data_property)

            # --------------------------------------------------------------------------------------
            # Verificar si la propiedad cuenta con rental units

            data_all_rentals = data_nodies.get('items_output', {}).get('rental', [])
            if data_all_rentals == []:
                self.logger.warning(
                    'La propiedad "%s" no tiene rental units. Cheqeuar', 
                    data_property['property_name']
                )
                continue

            # --------------------------------------------------------------------------------------
            # Recorrer los rental units que presenta la propiedad
            output_all_data_rental_units: list[dict] = self.search_data_rental(data_all_rentals)

            yield {
                'property': output_data_property,
                'all_rental_units': output_all_data_rental_units
            }

            break

    def extractor_data_property(self, data_property: dict):

        output_property: dict[str, str | list | dict] = {
            'property_features': data_property.get('property_features', []),
            'property_images': data_property.get('property_images', []),
            # 'property_name': data_property.get('property_name', ''),          No es seguro
            'property_phone': data_property.get('property_phone', ['']),
            'property_video': data_property.get('property_video', ''),
            'property_description_en': data_property.get('property_description_en', {}),
            'property_description_es': data_property.get('property_description_es', {}),
            'property_name_aux': data_property.get('info_hotel_property', {}).get('name', ''),
            'property_identity': data_property.get('info_hotel_property', {}).get('identity', ''),
            'property_telephone': data_property.get('info_hotel_property', {}).get('telephone', ''),
            'property_mobile': data_property.get('info_hotel_property', {}).get('mobile', ''),
            'property_email': data_property.get('info_hotel_property', {}).get('email', ''),
            'property_address': data_property.get('info_hotel_property', {}).get('address', ''),
            'property_state': data_property.get('info_hotel_property', {}).get('state', ''),
            'property_city': data_property.get('info_hotel_property', {}).get('city', ''),
            'property_url': data_property.get('info_hotel_property', {}).get('url', ''),
            'property_logo_url': data_property.get('info_hotel_property', {}).get('logoUrl', ''),
            'property_hotel_id': data_property.get('info_hotel_property', {}).get('hotelId', ''),
        }

        output_property['property_phone'] = output_property['property_phone'][0] if output_property['property_phone'] else ''

        output_property['property_description_en'] = " ".join([
            " ".join(output_property['property_description_en'].get('property_description_1_en', '')).strip(), 
            " ".join(output_property['property_description_en'].get('property_description_2_en', '')).strip()
        ]).strip()
        
        output_property['property_description_es'] = " ".join([
            " ".join(output_property['property_description_es'].get('property_description_1_es', '')).strip(), 
            " ".join(output_property['property_description_es'].get('property_description_2_es', '')).strip()
        ]).strip()

        for key, value in output_property.items():
            if all((key in ('property_features', 'property_images'), value in ('', [], None))):
                output_property[key] = []
                continue
            if value is None:
                output_property[key] = ''
                continue
            if isinstance(value, str):
                output_property[key] = clean_data(value)

        return output_property

    def create_output_property_model(self, output_data_property: dict) -> Property:
        # TODO: Crear el objeto con el model correspondiente para guardar la data extraida
        return output_data_property

    def search_data_rental(self, data_all_rentals: list[dict]):
        
        output_all_rentals = []

        for index_data_rental, data_rental in enumerate(data_all_rentals):
    
            if data_rental in ({}, None):
                self.logger.warning(
                    'En la posicion numero "%s" de la data json no contiene rental. Cheqeuar', 
                    index_data_rental
                )
                continue

            # ----------------------------------------------------------------------------------
            output_data_rental_unit = self.extractor_data_rental(data_rental)
            output_data_rental_unit: RentalUnits = self.create_output_rental_unit_model(output_data_rental_unit)

            output_all_rentals.append(output_data_rental_unit)
            break

        return output_all_rentals

    def extractor_data_rental(self, data_rental: dict):
        output_data_rental = {
            'rental_name': data_rental.get('rental_name', ''),
            'rental_id': data_rental.get('rental_id', ''),
            'rental_description_es': data_rental.get('rental_description', ''),
            'rental_images': data_rental.get('rental_images', {}).get('rental_image_url', ''),
        }

        for key, value in output_data_rental.items():
            if value is None:
                output_data_rental[key] = ''
                continue
            if isinstance(value, str):
                output_data_rental[key] = clean_data(value)

        return output_data_rental

    def create_output_rental_unit_model(self, output_data_rental_unit: dict) -> RentalUnits:
        # TODO: Crear el objeto con el model correspondiente para guardar la data extraida
        return output_data_rental_unit




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

def retrive_lodgerin_property(item, elements):
    data_property = item["items_output"].get("property", {})

    PropertyTypeId = get_id_from_name(
        elements["propertiesTypes"].data, "Apartment / Entire flat", "name_en"
    )
    element_feature = extract_id_label(elements["features"].data)

    features_id = search_feature_with_map(
        data_property["property_features"],
        element_feature,
        EquivalencesNodis.FEATURES,
    )

    if data_property.get("property_aux_address"):
        address_provider = (
            " ".join(data_property["property_aux_address"])
            if len(data_property["property_aux_address"]) < 3
            else " ".join(data_property["property_aux_address"][0:3])
        )
        address = search_location(address_provider)
    else:
        address = None

    reference_code = get_reference_code(data_property.get("property_name"))

    images = get_all_imagenes(data_property["property_images"])

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
            description_en=clear_descripcion(
                data_property["property_description_en"].get(
                    "property_description_2_en", []
                )
            ),
            description_es=clear_descripcion(
                data_property["property_description_es"].get(
                    "property_description_2_es", []
                )
            ),
            title_en=clear_descripcion(
                data_property["property_description_en"].get(
                    "property_description_1_en", []
                )
            ),
            title_es=clear_descripcion(
                data_property["property_description_es"].get(
                    "property_description_1_es", []
                )
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
        provider=Pages.nodis.value,
        providerRef=reference_code,
    )

    return property_items


def retrive_lodgerin_rental_units(
    data_property: Property, rental_unit: dict
):
    rental_name = clear_descripcion(rental_unit.get("rental_name", ""))
    rental_id = rental_unit.get("rental_id", None)
    rental_description = clear_descripcion(
        rental_unit.get("rental_description", "")
    ).replace(";", ",")
    rental_images = rental_unit.get("rental_images", {}).get("rental_image_url", "")

    data_rental_units = RentalUnits(
        Images=get_all_imagenes([rental_images]),
        PropertyId=data_property.id,
        referenceCode=f"{data_property.referenceCode}-{rental_id}",
        isActive=True,
        isPublished=True,
        Price=PriceItem(
            contractType=PaymentCycleEnum.MONTHLY.value,
            currency=CurrencyCode.EUR.value,
            amount=GlobalConfig.INT_ONE,  # TODO: Cambiar por el precio real
            depositAmount=GlobalConfig.INT_ONE,  # TODO: Cambiar por el precio real
            reservationAmount=GlobalConfig.INT_ZERO,
            minPeriod=GlobalConfig.INT_ONE,
            paymentCycle=PaymentCycleEnum.MONTHLY.value,
        ),
        Texts=Text(
            description_en=None,
            description_es=clear_descripcion(rental_description),
            title_en=None,
            title_es=clear_descripcion(rental_name),
        ),
        ExtraFeatures=filtrar_ids_validos(data_property.Features),
    )

    return data_rental_units

def load_json(file_path: Path) -> Any:
    """
    Carga un archivo JSON y retorna su contenido.
    """
    with file_path.open('r', encoding='utf-8') as f:
        return json.load(f)


def process_property(
    data: Dict[str, Any], elements: Dict[str, Any], api_key: str, exporter: CsvExporter
) -> None:
    """
    Procesa una propiedad y sus unidades de renta, guarda en API, exporta CSV y JSON.
    """
    prop_obj = retrive_lodgerin_property(data, elements)
    prop_id = funcs.save_property(prop_obj, api_key)
    prop_obj.id = prop_id
    create_json(prop_obj, Pages.nodis.value)
    Logger.info("Saved property %s", prop_id)

    rentals = data.get("items_output", {}).get("rental", [])
    if rentals:
        for rental in rentals:
            rent_obj = retrive_lodgerin_rental_units(prop_obj, rental)
            rent_id = funcs.save_rental_unit(rent_obj, api_key)
            rent_obj.id = rent_id
            create_json(rent_obj, Pages.nodis.value)
            Logger.info("Saved rental unit %s", rent_id)
            exporter.process_and_export_to_csv(prop_obj, rent_obj)
    else:
        exporter.process_and_export_to_csv(prop_obj)

