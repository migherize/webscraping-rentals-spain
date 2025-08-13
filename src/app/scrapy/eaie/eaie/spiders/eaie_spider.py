from pprint import pprint
import re
import scrapy
from scrapy import Selector
from scrapy.http import Response
from eaie.items import EaieItem
from eaie.enum_models import (
    ConfigXpathAllDepartments,
    ConfigXpathGroup,
    ConfigXpathPerson,
)



class EaieSpiderSpider(scrapy.Spider):
    name = "eaie_spider"
    start_urls = ["https://www.eaie.org/about-us/our-people.html"]

    def parse(self, response: Response):
        
        departments = response.xpath(ConfigXpathAllDepartments.SELECT_PEOPLE_DEPARTMENTS.value)
        if not departments:
            self.logger.warning('Sin coincidencias en el grupo de busqueda')
            return None

        for department in departments:
            yield scrapy.Request(
                department.get(),
                callback=self.parse_people_group,
                dont_filter=True
            )

    def parse_people_group(self, response: Response):
        
        # grupos o equipos

        # Caso donde existen etiquetas desplegables 
        label_group = response.xpath(ConfigXpathGroup.LABEL_GROUP.value)
        if label_group:
            department_info: dict = self._get_department_info(response)
            for group in label_group:
                team_info = self._get_group_info(group)
                people_group = group.xpath(ConfigXpathPerson.SELECTOR_ALL_PEOPLE.value)
                if people_group:
                    for person in people_group:
                        person_info = self._get_person_info(person)
                        output = person_info | team_info | department_info
                        output = self._get_output_data(output)
                        yield output
                        # break
            return None

        # Caso donde la informacion existen sin etiquetas desplegables 
        people_group = response.xpath(ConfigXpathPerson.SELECTOR_ALL_PEOPLE.value)
        if people_group:
            department_info: dict = self._get_department_info(response)
            for person in people_group:
                person_info = self._get_person_info(person)
                output = person_info | department_info
                output = self._get_output_data(output)
                yield output
                # break
            return None

        self.logger.warning('Existe un nuevo caso. Chequear la url: %s', [response.url])

    def _get_department_info(self, department: Response | Selector) -> dict:
        """ Extrae informacion del departamento """
        return {
            'department_url': department.url,
            'department_info':{
                'title': department.xpath(ConfigXpathGroup.MAIN_TITLE_GROUP.value).get(),
                'objective': self._join_description(department.xpath(ConfigXpathGroup.MAIN_OBJECTIVE_GROUP.value).getall()),
            }
        }
    
    def _get_group_info(self, group: Selector) -> dict:
        """ Extrae informacion del equipo o grupo """
        return {
            'group_info':{
                'title': group.xpath(ConfigXpathGroup.TITLE_GROUP.value).get(),
                'objective': self._join_description(group.xpath(ConfigXpathGroup.OBJECTIVE_GROUP.value).getall()),
            }
        }

    def _get_person_info(self, person: Selector) -> dict:
        """ Extrae informacion de las personas """
        return {
            'person_info': {
                'image': person.xpath(ConfigXpathPerson.IMAGE.value).get(),
                'name': person.xpath(ConfigXpathPerson.NAME.value).get(),
                'description': person.xpath(ConfigXpathPerson.DESCRIPTION.value).getall(),
                'social_media': person.xpath(ConfigXpathPerson.SOCIAL_MEDIA.value).get(),
            }
        }
    
    def _get_output_data(self, data: dict[str, str | dict[str, str]]) -> EaieItem:

        """ Crea el objeto de tipo EaieItem y lo retorna con los datos """

        data = self._get_title_and_description(data)

        item = EaieItem()
        item['department_name'] = self._clean_info(data.get('department_info', {}).get('title', ''))
        item['department_description'] = self._clean_info(data.get('department_info', {}).get('objective', ''))
        item['department_url'] = self._clean_info(data.get('department_url', ''))
        item['team_name'] = self._clean_info(data.get('group_info', {}).get('title', ''))
        item['team_description'] = self._clean_info(data.get('group_info', {}).get('objective', ''))
        item['person_foto'] = self._clean_info(data.get('person_info', {}).get('image', ''))
        item['person_name'] = self._clean_info(data.get('person_info', {}).get('name', ''))
        item['person_title'] = self._clean_info(data.get('person_info', {}).get('title', ''))
        item['person_description'] = self._clean_info(data.get('person_info', {}).get('description', ''))
        item['person_linked_in_url'] = self._clean_info(data.get('person_info', {}).get('social_media', ''))
        return item
    

    def _get_title_and_description(self, data: dict[str, str | dict]) -> dict[str, str | dict]:

        title_and_description = list(filter(None, data.get('person_info', {}).get('description', [])))
        data['person_info']['title'] = title_and_description[0]
        if len(title_and_description) == 1:
            data['person_info']['description'] = ''
            return data
        data['person_info']['description'] = self._join_description(title_and_description[1::])
        return data
    
    def _join_description(self, description: list[str]) -> str:
        """ Une la descripcion en un solo string """
        if not description:
            return ''
        return ' '.join(description)
    
    def _clean_info(self, data: str) -> str:
        data = (data or '').strip()
        data = re.sub(r' |\s{2,}', ' ', data).strip()
        data = re.sub(r'–', '-', data).strip()
        data = re.sub(r'’|‘', '\'', data).strip()
        data = re.sub(r'á', 'a', data).strip()
        data = re.sub(r'é', 'e', data).strip()
        data = re.sub(r'í', 'i', data).strip()
        data = re.sub(r'ó', 'o', data).strip()
        data = re.sub(r'ú', 'u', data).strip()
        return data