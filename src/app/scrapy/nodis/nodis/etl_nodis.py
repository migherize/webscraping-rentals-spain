from scrapy import Spider
from logging import Logger
from app.scrapy.common import read_json
from app.scrapy.nodis.nodis.spiders.nodis_spider import clean_data
from app.models.schemas import Property, RentalUnits



def etl_data_nodis(output_path: str, spider: Spider, logger: Logger):
    
    items: list[dict[str, str]] = read_json(output_path)
    if items == []:
        logger.warning('- No existe informacion en el archivo JSON para refinar')
        return None
    
    extractor_data_etl = ExtractorData(items, logger)
    output_data_nodis = list(extractor_data_etl.extractor_main_info())

    # TODO: Realzar el proceso de guardar la informacion para Lodgerin con la "output_data_nodis"


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
