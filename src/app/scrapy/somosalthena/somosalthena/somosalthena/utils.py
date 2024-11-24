from asyncio import constants
import re
import json
from scrapy import Spider
from pprint import pprint
from enum import Enum
from app.scrapy.common import clean_information_html, get_all_images
from app.models.schemas import Property, RentalUnits
import app.utils.constants as constants
from app.models.schemas import (
    Property,
    RentalUnits,
    ContractModel,
    Description,
    Image,
    LocationAddress,
    DatePayload,
    DatePayloadItem,
    ContractTypes,
    SpacesTypes,
    PropertyTypes,
    RentalUnitsTypes,
    Features,
    Furnitures,
    Languages,
    PensionTypes,
    ApiKey
)


class FeaturesSomosAlthena(Enum):
    
    FEATURES = {'Habitaciones', 'Cocina', 'Trasteros', 'Altillo', 'ZonasComunes', 'Terrazas', 'Gas', 'AccesoDiscapacitados', 'Agua', 'AdmiteMascotas', 'Microondas', 'Vigilancia24h', 'PiscinaPrivada', 'SofaCama', 'Sillas', 'AireAcondicionado', 'Despachos', 'CocinaAmueblada', 'Chimeneas', 'Amueblado', 'Exterior', 'Televisor', 'CajaFuerte', 'Conserje', 'Luz', 'Ascensor', 'Alarma', 'Cama', 'Calefaccion', 'Internet', 'Banos', 'ZonaInfantil', 'Armarios', 'Mesa', 'Lavadero', 'Horno'}
    EQUIVALENCES_FEATURES = {
        "Habitaciones": "Bedroom lock",
        "Banos": "Private bath",
        "AireAcondicionado": "Air conditioning",
        "Exterior": "Exterior",
        "Internet": "Wi-fi",
        "Cocina": "Kitchen",
        "PiscinaPrivada": "Swimming pool",
        "AdmiteMascotas": "Pets allowed",
        "Calefaccion": "Heating system",
        "Ascensor": "Lift",
        "ZonaInfantil": "Common areas",
        "Conserje": "24hr Concierge Reception",
        "Alarma": "Smoke alarm",
        "Vigilancia24h": "Video surveillance",
        "AccesoDiscapacitados": "Wheelchair access",
        "ZonaInfantil": "Playground",
        "Terrazas": "Terrace / balcony",
        "Gas": "Gas",
        "Agua": "Water",
        "Luz": "Electricity",
        "Amueblado": "Furnished",
        "ZonasComunes": "Common areas"
    }
    EQUIVALENCES_FURNITURES = {
        "Armarios": "Wardrobe",
        "CocinaAmueblada": "Fitted wardrobes",
        "Lavadero": "Washer",
        "CajaFuerte": "Closet",
        "Mesa": "Desk",
        "Sillas": "Chair",
        "Televisor": "Television",
        "Cama": "Double bed",
        "SofaCama": "Futon",
        "Horno": "Oven",
        "Microondas": "Microwave",
        "Trasteros": "Extra storage",
        "Despachos": "Filing Cabinet",
        "Altillo": "Bookshelf/Bookcase",
        "Chimeneas": "Iron"
    }



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
    with open(json_path_no_refined, "r") as file:
        all_data = json.load(file)
        for data_json in all_data:
            refined_data_json = refine_data_json(data_json)

            # TODO: Condiciones

            output_data.append(refined_data_json)
            # break

    return output_data


def refine_data_json(data_json: dict) -> dict:

    output_json_data = {
        "title": "",
        "referend_code": "",
        "cost": "",
        "area_building": "",
        "area_utils": "",
        "bedrooms": "",
        "bathrooms": "",
        "all_titles": {
            "spanish": "",
            "catalan": "",
            "english": "",
            "french": "",
        },
        "all_descriptions_short": {
            "spanish": "",
            "catalan": "",
            "english": "",
            "french": "",
        },
        "all_descriptions": {
            "spanish": "",
            "catalan": "",
            "english": "",
            "french": "",
        },
        "address": {
            "Numero": "",
            "Direccion": "",
            "Zona": "",
            "Provincia": "",
            "Poblacion": "",
            "CodigoPostal": "",
            "latitude": "",
            "longitude": "",
        },
        "images": [],
        "features": []
    }

    output_json_data["title"] = data_json["Titulo"]
    output_json_data["referend_code"] = data_json["Referencia"]
    output_json_data["cost"] = data_json["Precio"]
    output_json_data["area_building"] = data_json["MetrosConstruidos"]
    output_json_data["area_utils"] = data_json["MetrosUtiles"]
    
    output_json_data["bedrooms"] = data_json["Habitaciones"]
    output_json_data["bathrooms"] = data_json["Banos"]

    output_json_data["address"]["Numero"] = data_json["Numero"]
    output_json_data["address"]["Direccion"] = data_json["Direccion"]
    output_json_data["address"]["Zona"] = data_json["Zona"]
    output_json_data["address"]["Provincia"] = data_json["Provincia"]
    output_json_data["address"]["Poblacion"] = data_json["Poblacion"]
    output_json_data["address"]["CodigoPostal"] = data_json["CodigoPostal"]
    output_json_data["address"]["latitude"] = data_json["Latitud"]
    output_json_data["address"]["longitude"] = data_json["Longitud"]

    output_json_data["output_address"] = get_address(output_json_data["address"])

    all_titles = ("Titulo", "TituloCa", "TituloEn", "TituloFr")
    output_json_data = get_all_multidata(
        all_titles, data_json, output_json_data, "all_titles"
    )

    all_description = (
        "DescripcionAmpliada",
        "DescripcionAmpliadaCa",
        "DescripcionAmpliadaEn",
        "DescripcionAmpliadaFr",
    )
    output_json_data = get_all_multidata(
        all_description, data_json, output_json_data, "all_descriptions"
    )

    all_description_short = (
        "Descripcion",
        "DescripcionCa",
        "DescripcionEn",
        "DescripcionFr",
    )
    output_json_data = get_all_multidata(
        all_description_short, data_json, output_json_data, "all_descriptions_short"
    )
    output_json_data["images"] = get_all_images(data_json["Fotos"])
    output_json_data["features"] = get_all_features(data_json)
    return output_json_data


def get_address(address: dict) -> dict:
    aux_address = {
        "number": address["Numero"],
        "lat": address["latitude"],
        "lon": address["longitude"],
        "fullAddress": "",
        "address": "",
        "city": address["Poblacion"],
        "street": address["Direccion"],
        "state": address["Provincia"],
        "postalCode": address["CodigoPostal"],
        "country": "",
        "countryCode": "",
        "prefixPhone": "",
    }
    aux_address["address"] = (
        f"{aux_address['number']} "
        f"{aux_address['street']}, "
        f"{aux_address['city']}, "
        f"{aux_address['state']}, "
        f"{aux_address['postalCode']}"
    )
    aux_address["address"] = re.sub(r"\s{2,}", " ", aux_address["address"])
    aux_address["fullAddress"] = aux_address["address"]
    return aux_address


def get_all_multidata(
    multidata: tuple[str],
    data_json: dict,
    output_json_data: dict,
    key_main: str,
):
    for data, key_data_json in zip(multidata, output_json_data[key_main].keys()):
        output_json_data[key_main][key_data_json] = clean_information_html(
            data_json[data]
        )

    return output_json_data


def get_all_features(data_json: dict):

    all_feature_somosalthena = FeaturesSomosAlthena.FEATURES.value

    output_info_feature = {}
    for feature_somosalthena in all_feature_somosalthena:
        try:
            if data_json[feature_somosalthena] in (0, "0", '', None, "None"):
                output_info_feature[feature_somosalthena] = False
            else:
                output_info_feature[feature_somosalthena] = True
        except:
            output_info_feature[feature_somosalthena] = False

    return output_info_feature



def get_id_from_name(data_dict: dict, name: str, key_name: str) -> int:
    """
    Busca el ID asociado a un nombre en un diccionario con estructura similar a "property_types" o "pension_types".

    Args:
        data_dict (dict): Diccionario que contiene una lista de datos bajo la llave "data".
        name (str): Nombre que se desea buscar.

    Returns:
        int: El ID asociado al nombre, si se encuentra. De lo contrario, retorna None.
    """
    for item in data_dict.get("data", []):
        if item.get(key_name) == name:
            return item.get("id")
    return None


def process_descriptions(
    all_descriptions: dict, all_titles: dict, languages_dict: dict
) -> list:
    """
    Procesa las descripciones en varios idiomas y devuelve una lista de diccionarios con el ID del idioma.

    Args:
        all_descriptions (dict): Diccionario con las descripciones en diferentes idiomas.
        languages_dict (dict): Diccionario con la lista de idiomas.

    Returns:
        list: Lista de diccionarios con el formato deseado, con ID de idioma y las descripciones.
    """
    result = []

    for (lang_key_desc, description), (lang_key_title, title) in zip(
        all_descriptions.items(), all_titles.items()
    ):
        if lang_key_desc == lang_key_title:
            language_id = get_id_from_name(
                languages_dict, lang_key_desc.capitalize(), "name_en"
            )
            if language_id:
                result.append(
                    {
                        "LanguagesId": language_id,
                        "title": title,
                        "description": description,
                    }
                )
    return result


def search_feature_with_map(items_features: dict, elements_features: list[dict]):

    for data_feature in elements_features:
        id_feature = data_feature["id"]
        name_feature = data_feature["name"]

        # TODO: Pendiente con el match

def retrive_lodgerin(items, elements):
    PropertyTypeId = get_id_from_name(elements["property_types"], "Host family", "name")
    PensionTypeId = get_id_from_name(elements["pension_types"], "Full board", "name")
    descriptions = process_descriptions(
        items["all_descriptions"], items["all_titles"], elements["languages"]
    )
    features = search_feature_with_map(items['features'], elements['features']['data'])

    data_property = Property(
        name=items["title"],
        description=items["all_descriptions_short"]["spanish"],
        referenceCode=items["referend_code"],
        # minAge=items[''],
        # maxAge=items[''],
        areaM2=items["area_building"],
        areaM2Available=items["area_utils"],
        # maxOccupancy=items[''],
        # dateLastReform=items[''],
        # tenantGender=items[''],
        cancellationPolicy=constants.CANCELLATION_POLICY,
        rentalType=constants.RENTAL_TYPE,
        isActive=True,
        isPublished=True,
        Features=items[""],  # TODO: add Features
        # Languages=items[''],
        # videoUrl=items[''],
        # tourUrl=items[''],
        PropertyTypeId=PropertyTypeId,
        PensionTypeId=PensionTypeId,
        Descriptions=descriptions,
        Images=items["images"],
        Location=items["output_address"],
    )

    data_rental_units = RentalUnits(
        PropertyId=items[""],
        referenceCode=items[""],
        areaM2=items[""],
        areaM2Available=items[""],
        maxCapacity=items[""],
        urlICalSync=items[""],
        bedType=items[""],
        Features=items[""],
        Furnitures=items[""],
        isActive=items[""],
        isPublished=items[""],
        ContractsModels=items[""],
        Descriptions=items[""],
        Images=items[""],
    )
    return data_property, data_rental_units
