import re
from scrapy import Spider
from logging import Logger
from app.scrapy.common import read_json


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

    output_property: dict[str, str | list] = {
        'property_features': data_property.get('property_features', []),
        'property_images': data_property.get('property_images', []),
        'property_name': data_property.get('property_name', ''),
        'property_phone': data_property.get('property_phone', [''])[0],
        'property_video': data_property.get('property_video', ''),
        'description_en': '',
        'description_es': '',
    }

    description_en_1: str = data_property.get('property_description_en', {}).get('property_description_1_en', '').strip()
    description_en_2: str = data_property.get('property_description_en', {}).get('property_description_2_en', '').strip()
    output_property['description_en'] = (description_en_1 + ' ' + description_en_2).strip()
    
    description_es_1: str = data_property.get('property_description_es', {}).get('property_description_1_es', '').strip()
    description_es_2: str = data_property.get('property_description_es', {}).get('property_description_2_es', '').strip()
    output_property['description_es'] = (description_es_1 + ' ' + description_es_2).strip()

    for key, value in output_property.items():
        if all((key in ('property_features', 'property_images'), value in ('', [], None))):
            output_property[key] = []
            continue
        if value is None:
            output_property[key] = ''
            continue

    return output_property


def extractor_data_rental(data_rental: dict):
    pprint(data_rental)
    pass