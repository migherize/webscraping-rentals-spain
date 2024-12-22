import re


def clean_city_name(data: list[str]) -> str:
    if data and isinstance(data, list):
        return data[0].strip()
    return ''

def clean_description_city(data: str) -> str:
    return data.strip()

def clean_url_city(data: str) -> str:
    return data.strip()

def clean_yugo_space_name(data: str) -> str:
    return data.strip()

def clean_description_yugo_space(data: str) -> str:
    return data.strip()

def clean_url_yugo_space(data: str) -> str:
    return data.strip()

def clean_property_name(data: list[str]) -> str:
    if data and isinstance(data, list):
        return data[0].strip()
    return ''

def clean_address_contact_and_email(data: list[str]) -> str:
    """
    retorna solo la direccion
    """
    if data and isinstance(data, list):
        address = ", ".join(data)
        address = re.sub(r'Tel:.+', '', address).strip()
        return address
    return ''

def clean_residence_description(data: list[str]) -> str:
    if data and isinstance(data, list):
        return re.sub(r' ', ' ', "".join(data))
    return ''

def clean_student_rooms(data: str) -> str:
    return data.strip()

def clean_all_feature(data: list[str]) -> list[str]:
    if data and isinstance(data, list):
        return list(map(
            lambda x: re.sub(r'\n|\r', '', x),
            data
        ))
    return ['']

def clean_latitud(data: str) -> str:
    return data.strip()

def clean_longitud(data: str) -> str:
    return data.strip()

def clean_all_images(data: list[str]) -> list[str]:
    if data and isinstance(data, list):
        return data
    return ['']

def clean_data_languages(data: list) -> list:
    return data