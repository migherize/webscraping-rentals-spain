from logging import Logger
from pprint import pprint
from scrapy import Spider
from app.scrapy.common import read_json



def etl_data_livensaliving(output_path_data: str, spider: Spider, logger: Logger):
    
    # Obtener la data extraida de la arana
    all_data = read_json(output_path_data)

    # Verificar si hay informacion extraida o existe el documento
    if not all_data:
        logger.warning('No existe data o el archivo para refinar. Chequear')
        return None
    
    extractor = ExtractorLivensaliving(logger)
    extractor.parse_main_data(all_data)
    

class ExtractorLivensaliving:

    def __init__(self, logger: Logger):
        self.logger: Logger = logger

    def parse_main_data(self, all_data: list[dict]):
        
        for index_property, info_property in enumerate(all_data):
            main_data_property: dict = info_property.get('items_output', {}).get("main_data_property", {})
            main_data_property |= info_property.get('items_output', {}).get("info_aux_property", {})
            main_data_rental: dict = info_property.get('items_output', {}).get("main_data_rental", {})
            
            if not main_data_property:
                self.logger.warning("La propiedad numero: %s, no presenta informacion. Chequear", index_property)
                continue

            # Informacion de la propiedad extraida
            output_property: dict = self.get_data_property(main_data_property)

            url_rental_units = main_data_rental.get("url_rental_units", None)
            all_rental_units = main_data_rental.get("all_rental_units", None)
            if all_rental_units is None:
                # Guardar la informacion de la propiedad
                self.logger.info('No presenta rental_units la propiedad: %s', url_rental_units)
                continue

            # Recorrer todos los rental units que contiene la propiedad
            for index_rental_unit, info_rental_unit in enumerate(all_rental_units):
                self.get_data_rental_unit(info_rental_unit)
                break

            break

    def get_data_property(self, property_data: dict) -> dict:
        output_property = {
            'property_url': property_data.get("url", ''),
            'property_name': property_data.get("name", [])[0],
            'property_title': property_data.get("title", [])[0],
            'property_address': get_property_address(property_data.get('address', [])),
            'property_images': property_data.get('images', []),
            'property_feature': property_data.get('feature', []),
            'property_description': get_description(
                property_data.get('description', []),
                property_data.get('description_1', []),
                property_data.get('description_2', []),
            ),
        }
        return output_property

    def get_data_rental_unit(self, rental_unit_data: dict) -> dict[str]:

        # TODO: Pendiente

        # pprint(rental_unit_data)
        rental_unit_data.get("name_1", "")
        rental_unit_data.get("name_2", "")
        rental_unit_data.get("description", "")
        rental_unit_data.get("features", [])
        rental_unit_data.get("images", [])
        rental_unit_data.get("all_types", [])       # Los rental tienen varios modelos, aqui se tiene: el nombre, la descripcion, el pago mensual y si es anual o no

        output_rental_unit = {
            # TODO: Chequear lo que se agregara
        }
        return output_rental_unit


def get_property_address(address: list[str]) -> str:
    if not address or len(address) < 2:
        return None
    return " ".join(address[1::])


def get_description(description_0: list[str], description_1: list[str], description_2: list[str]):
    description_0 = " ".join(description_0).strip()
    description_1 = " ".join(description_1).strip()
    description_2 = " ".join(description_2).strip()
    output_description = ". ".join([
        description_0, 
        description_1, 
        description_2
    ]).strip()
    return output_description