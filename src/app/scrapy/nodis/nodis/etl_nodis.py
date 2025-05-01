import re
from scrapy import Spider
from logging import Logger
from app.scrapy.common import read_json
from app.scrapy.nodis.nodis.spiders.nodis_spider import clean_data

from pprint import pprint


def etl_data_nodis(output_path: str, spider: Spider, logger: Logger):
    
    items: list[dict[str, str]] = read_json(output_path)
    if items == []:
        logger.warning('- No existe informacion en el archivo JSON para refinar')
        return None

    for index_data_property, data_nodies in enumerate(items):
        data_property = data_nodies.get('items_output', {}).get('property', {})
        data_all_rentals = data_nodies.get('items_output', {}).get('rental', [])

        if data_property in ({}, None):
            logger.warning('En la posicion numero "%s" de la data json no contiene propiedad. Cheqeuar', index_data_property)
            continue

        logger.info('Refinando la propiedad: "%s"', data_property['property_name'])

        output_data_property = extractor_data_property(data_property)

        if data_all_rentals == []:
            logger.warning('La propiedad "%s" no tiene rental units. Cheqeuar', data_property['property_name'])
            continue

        for index_data_rental, data_rental in enumerate(data_all_rentals):
    
            if data_rental in ({}, None):
                logger.warning('En la posicion numero "%s" de la data json no contiene propiedad. Cheqeuar', index_data_property)
                continue

            extractor_data_rental(data_rental)
            break
        break

def extractor_data_property(data_property: dict):

    output_property: dict[str, str | list | dict] = {
        'property_features': data_property.get('property_features', []),
        'property_images': data_property.get('property_images', []),
        # 'property_name': data_property.get('property_name', ''),  No es seguro
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

    pprint(output_property)
    return output_property


def extractor_data_rental(data_rental: dict):
    pprint(data_rental)
    pass