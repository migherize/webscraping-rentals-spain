import re
import json
import scrapy
from os import path
from pathlib import Path
from scrapy import Selector
from app.scrapy.livensaliving.livensaliving.items import LivensalivingItem
from app.scrapy.nafsa.nafsa.config_enum import (
    ConfigGeneral,
    XpathTable,
    XpathInfoAttendees,
)


class NafsaSpiderSpider(scrapy.Spider):
    name = "nafsa_spider"

    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "AUTOTHROTTLE_ENABLED": True,
        "LOG_LEVEL": "INFO",
    }

    def __init__(self, context=None, *args, **kwargs):
        super(NafsaSpiderSpider, self).__init__(*args, **kwargs)

        item_input_output_archive: dict[str, str] = {
            "output_folder_path": "./",
            "output_folder_name": "nafsa_output",
            "file_name": "nafsa.json",
            "processed_name": "nafsa_refined.json",
            "refine": '0',
        }

        self.items_spider_output_document = {
            key_data: kwargs.pop(key_data, item_input_output_archive[key_data])
            for key_data in item_input_output_archive.keys()
        }
        self.items_spider_output_document["output_folder"] = path.join(
            self.items_spider_output_document["output_folder_path"],
            self.items_spider_output_document["output_folder_name"],
        )

        Path(self.items_spider_output_document["output_folder"]).mkdir(
            parents=True, exist_ok=True
        )
        self.context = json.loads(context) if context else {}

    def start_requests(self):
        if self.items_spider_output_document['refine'] == '1':
            self.logger.info("Proceso de refinado para: %s", self.name)
            return []

        return [
            scrapy.FormRequest(
                ConfigGeneral.URL_LOGIN.value,
                formdata={
                    "AccountEmail": ConfigGeneral.USER_NAME.value,
                    "AccountKey": ConfigGeneral.PASSWORD.value,
                },
                headers=ConfigGeneral.HEADERS_LOGIN.value,
                method='POST'
            )
        ]

    def parse(self, response: Selector):

        # Confirmar si se logro iniciar la sesion

        if response.status != 200:
            self.logger.warning('No se logro realizar el login')
            return None

        # Busqueda de la tabla
        yield scrapy.Request(
            ConfigGeneral.URL_MAIN.value,
            callback=self.parse_main_table,
        )

    def parse_main_table(self, response: Selector):
        
        table = response.xpath(XpathTable.MAIN_TABLE.value)
        
        if not table:
            self.logger.warning('No se obtuvo la tabla para los Attendees')
            return None

        for index, row in enumerate(table.xpath(XpathTable.ROWS.value)):
            id_attendee = row.xpath(XpathTable.URL_ATTENDEES.value).get()
            if id_attendee is None:
                continue
            new_id_attendee = get_id_attendee(id_attendee)
            yield scrapy.Request(
                get_url_info_attendee(new_id_attendee),
                callback=self.parse_info_attendee,
                meta={'new_id_attendee': new_id_attendee},
                dont_filter=True,
            )

    def parse_info_attendee(self, response: Selector):
        new_id_attendee = response.meta.get('new_id_attendee')
        info_attendee = {
            'id_attendee': new_id_attendee,
            'url_info_attendee': response.url,
            'url_email_attendee': '',
            'data_attendee': {
                "name": response.xpath(XpathInfoAttendees.NAME.value).getall(),
                "title": response.xpath(XpathInfoAttendees.TITLE.value).getall(),
                "address": response.xpath(XpathInfoAttendees.ADDRESS.value).getall(),
                "mobile_phone": response.xpath(XpathInfoAttendees.MOBILE_PHONE.value).getall(),
                "mobile_office": response.xpath(XpathInfoAttendees.MOBILE_OFFICE.value).getall(),
                "description": response.xpath(XpathInfoAttendees.DESCRIPTION.value).getall(),
                "email": '',
            }
        }
        info_attendee['data_attendee'] |= {
            key: response.xpath(value).getall()
            for key, value in XpathInfoAttendees.OTHER_INFORMATION.value.items()
        }
        url_email = get_url_email_attendee(new_id_attendee)
        if url_email is None:
            output_items = LivensalivingItem()
            output_items['items_output'] = info_attendee
            yield output_items
            return None

        yield scrapy.Request(
            url_email,
            dont_filter=True,
            callback=self.parse_email_attendee,
            meta={'info_attendee': info_attendee}
        )

    def parse_email_attendee(self, response: Selector):
        info_attendee = response.meta.get('info_attendee')
        info_attendee['url_email_attendee'] = response.url
        info_attendee['data_attendee']['email'] = response.xpath(XpathInfoAttendees.EMAIL.value).get()
        output_items = LivensalivingItem()
        output_items['items_output'] = info_attendee
        yield output_items

def get_id_attendee(id_attendee: str) -> str:
    id_attendee = id_attendee.replace("ajaxcalls/AccountInfo.asp?", '')
    return id_attendee

def get_url_info_attendee(id_attendee: str) -> str:
    url_info_attendee = (
        ConfigGeneral.BASE_URL_SEARCH.value +
        id_attendee +
        ConfigGeneral.MODE_ACCOUNT_INFO.value
    )
    return url_info_attendee

def get_url_email_attendee(id_attendee: str) -> str:
    search_id_attendee = re.search(r"ID=(\d+)&", id_attendee)
    if search_id_attendee:
        id_attendee = 'userID=' + search_id_attendee.group(1)
        url_email_attendee = path.join(
            ConfigGeneral.BASE_URL_SEARCH.value +
            id_attendee +
            ConfigGeneral.MODE_EMAIL.value
        )
        return url_email_attendee
    return None