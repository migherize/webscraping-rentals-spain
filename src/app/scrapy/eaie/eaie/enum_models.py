from enum import Enum


class ConfigXpathAllDepartments(Enum):
    SELECT_PEOPLE_DEPARTMENTS = '//a[contains(text(), "View more")]/@href'


class ConfigXpathGroup(Enum):
    LABEL_GROUP = '//div[@class="collapsible-item"]'

    # Informacion principal del departamento
    MAIN_TITLE_GROUP = '//h1/text()'
    MAIN_OBJECTIVE_GROUP = '//h1/../div/p//text()'
    
    # Informacion del grupo o equipo (Este caso se presenta en los labels desplegables)
    TITLE_GROUP = './h4/a/text()[1]'
    OBJECTIVE_GROUP = './div/p/text()'


class ConfigXpathPerson(Enum):
    SELECTOR_ALL_PEOPLE = './/div[@class="profile"]//div[@class="modal fade"]'
    IMAGE = './/img/@src'
    NAME = './/div[@class="profile-content"]//h3/text()'
    DESCRIPTION = './/div[@class="profile-content"]//p//text()'
    SOCIAL_MEDIA = './/div[@class="profile-content"]//a[contains(@href, "linkedin")]/@href'
