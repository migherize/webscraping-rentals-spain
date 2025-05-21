from os import path
import re
import pandas as pd
from logging import Logger
from scrapy import Spider
from app.scrapy.common import read_json


def etl_data_nafsa(output_path_data_not_refine: str, spider: Spider, logger: Logger):
    
    # Obtener la data extraida de la arana
    all_data = read_json(output_path_data_not_refine)

    # Verificar si hay informacion extraida o existe el documento
    if not all_data:
        logger.warning('No existe data o el archivo para refinar. Chequear')
        return None
    
    output_data_lodgerin = {
        "name": [],
        "title": [],
        "address": [],
        "phone_office": [],
        "mobile_phone": [],
        "description": [],
        "email": [],
        "type_of_organization": [],
        "professional_area": [],
        "partnership_interests": [],
        "organization_or_provider": [],
        "url_source_attendee": [],
    }

    for index, data in enumerate(all_data):
        
        items_output: dict = data.get('items_output', {})

        if items_output == {}:
            continue
        
        data_attendee: dict = items_output.get('data_attendee', {})
        if data_attendee == {}:
            continue

        id_attendee: str = items_output.get('id_attendee', '')
        url_email_attendee: str = items_output.get('url_email_attendee', '') 

        url_info_attendee: str = items_output.get('url_info_attendee', '') 
        output_attendee = get_data_attendee(data_attendee)
        
        output_data_lodgerin["name"].append(output_attendee['name'])
        output_data_lodgerin["title"].append(output_attendee['title'])
        output_data_lodgerin["address"].append(output_attendee['address'])
        output_data_lodgerin["phone_office"].append(output_attendee['phone_office'])
        output_data_lodgerin["mobile_phone"].append(output_attendee['mobile_phone'])
        output_data_lodgerin["description"].append(output_attendee['description'])
        output_data_lodgerin["email"].append(output_attendee['email'])
        output_data_lodgerin["type_of_organization"].append(output_attendee['type_of_organization'])
        output_data_lodgerin["professional_area"].append(output_attendee['professional_area'])
        output_data_lodgerin["partnership_interests"].append(output_attendee['partnership_interests'])
        output_data_lodgerin["organization_or_provider"].append(output_attendee['organization_or_provider'])
        output_data_lodgerin["url_source_attendee"].append(url_info_attendee)

    # Save data csv
    output_path_data_refine = path.join(spider.items_spider_output_document["output_folder"], 'nafsa_refine.csv')
    df = pd.DataFrame(output_data_lodgerin, dtype='string')
    df.to_csv(
        output_path_data_refine,
        encoding='utf8',
        index=False
    )

def get_data_attendee(data: dict) -> dict[str, str]:
    output = {
        'name': data.get('name', [''])[0],
        'title': join_data(data.get('title', [])),
        'address': get_address(data.get('address', [])),
        'phone_office': get_phone(data.get('mobile_office', [])),
        'mobile_phone': get_phone(data.get('mobile_phone', [])),
        'email': data.get('email', ''),
        'description': join_data(data.get('description', [])),
        'type_of_organization': join_data(data.get('Type of Organization I work for:', '')),
        'professional_area': join_data(data.get('My Area of Professional Responsibility is:', '')),
        'partnership_interests': join_data(data.get('My Organization is Interested in Partnership Opportunities to:', '')),
        'organization_or_provider': join_data(data.get('My Organization Provides:', '')),
        # '': data.get('', ''),
    }

    check_fields(output)

    return output


def check_fields(output: dict[str, str]) -> None:

    if re.search(r"^My\s", output['description']):
        output['partnership_interests'] = output['professional_area']
        output['professional_area'] = output['type_of_organization']
        output['type_of_organization'] = output['organization_or_provider']
        output['organization_or_provider'] = output['description']
        output['description'] = ''

    output['type_of_organization'] = re.sub("Type of Organization I work for:", '', output['type_of_organization']).strip()
    output['professional_area'] = re.sub("My Area of Professional Responsibility is:", '', output['professional_area']).strip()
    output['partnership_interests'] = re.sub("My Organization is Interested in Partnership Opportunities to:", '', output['partnership_interests']).strip()
    output['organization_or_provider'] = re.sub("My Organization Provides:", '', output['organization_or_provider']).strip()

def get_phone(data_phone: list[str]) -> str:
    if data_phone == []:
        return ''
    return clean_data(data_phone[0].split(':')[-1])


def get_address(data_address: list[str]) -> str:
    if data_address == []:
        return ''
    return clean_data(data_address[0])


def join_data(data: list[str]) -> str:
    if data == []:
        return ''
    return clean_data(" ".join(data))


def clean_data(data: str) -> str:
    data = re.sub(r'\t|\r|\n', '', data).strip()
    data = re.sub(r'\s{2,}', ' ', data).strip()
    return data
