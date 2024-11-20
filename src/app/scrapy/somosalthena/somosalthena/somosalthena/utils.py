import re
import json
from scrapy import Spider
from pprint import pprint
from app.scrapy.common import clean_information_html, get_all_images


def get_data_json(object_spider: Spider, json_path_no_refined: str) -> list[dict]:
    """
    object_spider:
        keys:
            "output_folder_path"
            "output_folder_name"
            "file_name"
            "processed_name"
            "refine"
            "output_folder"
    """

    output_data = []

    # Leer un archivo JSON
    with open(json_path_no_refined, 'r') as file:
        all_data = json.load(file)
        for data_json in all_data:
            refined_data_json = refine_data_json(data_json)

            # TODO: Condiciones

            output_data.append(refined_data_json)
            # break

    return output_data


def refine_data_json(data_json: dict) -> dict:

    output_json_data = {
        "title": '',
        "referend_code": '',
        "cost": '',
        "area": '',
        "bedrooms": '',
        "bathrooms": '',
        "all_titles": {
            'spanish': '',
            'catalan': '',
            'english': '',
            'french': '',
        },
        "all_descriptions": {
            'spanish': '',
            'catalan': '',
            'english': '',
            'french': '',
        },
        # "all_status": {
        #     'spanish': '',
        #     'catalan': '',
        #     'english': '',
        #     'french': '',
        # },
        'address': {
            "Numero": '',
            "Direccion": '',
            "Zona": '',
            "Provincia": '',
            "Poblacion": '',
            "CodigoPostal": '',
            "latitude": '',
            "longitude": '',
        },
        'images': [],
    }

    output_json_data["title"] = data_json['Titulo']
    output_json_data["referend_code"] = data_json['Referencia']
    output_json_data["cost"] = data_json['Precio']
    output_json_data["area"] = data_json['MetrosConstruidos']
    output_json_data["bedrooms"] = data_json['Habitaciones']
    output_json_data["bathrooms"] = data_json['Banos']
    
    output_json_data["address"]["Numero"] = data_json["Numero"]
    output_json_data["address"]["Direccion"] = data_json["Direccion"]
    output_json_data["address"]["Zona"] = data_json["Zona"]
    output_json_data["address"]["Provincia"] = data_json["Provincia"]
    output_json_data["address"]["Poblacion"] = data_json["Poblacion"]
    output_json_data["address"]["CodigoPostal"] = data_json["CodigoPostal"]
    output_json_data["address"]["latitude"] = data_json['Latitud']
    output_json_data["address"]["longitude"] = data_json['Longitud']

    output_json_data["output_address"] = get_address(output_json_data["address"])

    all_titles = ('Titulo', 'TituloCa', 'TituloEn', 'TituloFr')
    output_json_data = get_all_multidata(all_titles, data_json, output_json_data, 'all_titles')

    all_description = (
        "DescripcionAmpliada", "DescripcionAmpliadaCa", 
        "DescripcionAmpliadaEn", "DescripcionAmpliadaFr"
    )

    output_json_data = get_all_multidata(all_description, data_json, output_json_data, 'all_descriptions')
    output_json_data["images"] = get_all_images(data_json['Fotos'])

    return output_json_data


def get_address(address: dict) -> dict:
    aux_address = {
        'number': address['Numero'],
        'lat': address['latitude'],
        'lon': address['longitude'],
        'fullAddress': '',
        'address': '',
        'city': address['Poblacion'],
        'street': address['Direccion'],
        'state': address['Provincia'],
        'postalCode': address['CodigoPostal'],
        'country': '',
        'countryCode': '',
        'prefixPhone': '',
    }
    aux_address['address'] = (
        f"{aux_address['number']} "
        f"{aux_address['street']}, "
        f"{aux_address['city']}, "
        f"{aux_address['state']}, "
        f"{aux_address['postalCode']}"
    )
    aux_address['address'] = re.sub(r'\s{2,}', ' ', aux_address['address'])
    aux_address['fullAddress'] = aux_address['address']
    return aux_address

def get_all_multidata(
        multidata: tuple[str],
        data_json: dict,
        output_json_data: dict,
        key_main: str,
):
    for data, key_data_json in zip(multidata, output_json_data[key_main].keys()):
        output_json_data[key_main][key_data_json] = clean_information_html(data_json[data])
        
    return output_json_data
