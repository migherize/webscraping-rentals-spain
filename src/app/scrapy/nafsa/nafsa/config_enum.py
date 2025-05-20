from enum import Enum
from app.config.settings import TokenConfig

class ConfigGeneral(Enum):
    URL_MAIN = "https://nafsa2025.eventscribe.net/Userlist.asp?pfp=UserList"
    URL_LOGIN = "https://nafsa2025.eventscribe.net/login/baseLoginRegProc.asp"
    USER_NAME = TokenConfig.USERNAME_NAFSA
    PASSWORD = TokenConfig.PASSWORD_NAFSA

    BASE_URL_SEARCH = "https://nafsa2025.eventscribe.net/fsPopup.asp?"
    MODE_ACCOUNT_INFO = "&mode=accountInfo"
    MODE_EMAIL = "&mode=accountEmail"

    HEADERS_LOGIN = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "es-419,es;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "max-age=0",
        "content-type": "application/x-www-form-urlencoded",
        "priority": "u=0, i",
        "sec-ch-ua": "\"Chromium\";v=\"136\", \"Google Chrome\";v=\"136\", \"Not.A/Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1"
    }

class XpathTable(Enum):
    MAIN_TABLE = '//ul[@id="userList"]'
    ROWS = './li'
    URL_ATTENDEES = './/@href'


class XpathInfoAttendees(Enum):
    NAME = '//h1/text()'
    TITLE = '//h1/../p[1]//text()'
    ADDRESS = '//h1/../p[2]//text()'
    MOBILE_PHONE = "//p[contains(text(), 'Mobile Phone:')]/text()"
    MOBILE_OFFICE = "//p[contains(text(), 'Office Phone:')]/text()"
    DESCRIPTION = '//h1/../div[1]//text()'
    OTHER_INFORMATION = {
        'My Organization Provides:': '//h1/../div[2]//text()',
        'Type of Organization I work for:': '//h1/../div[3]//text()',
        'My Area of Professional Responsibility is:': '//h1/../div[4]//text()',
        'My Organization is Interested in Partnership Opportunities to:': '//h1/../div[5]//text()',
    }
    EMAIL = "//input[@id='emailTo']/@value"
