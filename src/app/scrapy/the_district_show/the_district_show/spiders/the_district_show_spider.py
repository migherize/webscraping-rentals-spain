import scrapy
from scrapy import Selector
from scrapy.http import Response
from the_district_show.items import TheDistrictShowItem

from enum import Enum


class ConfigXpath(Enum):
    ALL_SPEAKERS = "//div[contains(text(), 'Meet all our speakers')]/../div/a/@href"

    SPEAKER_NAME = "//h1/text()"
    URL_LINKEDIN = "//li/a[contains(@href, 'linkedin')]/@href"
    URL_WHATSAPP = "//a[contains(@href, 'api.whatsapp')]/@href"
    URL_X = "//a[contains(@href, 'twitter')]/@href"
    COMPANY_INFO = "//div[contains(text(), 'Position:')]/.."
    
    POSITION = "div[2]/text()"
    COMPANY = "div[4]/text()"

    DESCRIPTION = "//div[contains(text(), 'Sessions')]/../div[6]/p/text()"



class SessionXpath(Enum):
    ALL_SESSIONS = '//section/div'
    CONTAINER = ".//div[starts-with(@id, 'sesion-')]"
    DATE = ".//p[contains(@class, 'font-bold')]/text()"
    TIME = ".//span[contains(text(), '-')]/text()"
    ADDRESS = ".//a[contains(@href, 'javascript:void')]/text()"
    NAME = ".//a[contains(@class, 'session-title')]/text()"


class TheDistrictShowSpiderSpider(scrapy.Spider):
    name = "the_district_show_spider"
    start_urls = [
        "https://www.thedistrictshow.com/agenda-speakers/"
    ]

    def parse(self, response: Response):

        all_speakers = response.xpath(ConfigXpath.ALL_SPEAKERS.value)

        if not (all_speakers):
            self.logger.warning("No speakers found")
            return None

        for index, speaker in enumerate(all_speakers):

            # if index == 5: break

            url_speaker = speaker.get()
            if not (url_speaker):
                self.logger.warning(f"No URL found for speaker at index {index}")
                continue

            yield scrapy.Request(
                url=url_speaker, callback=self.parse_speaker, dont_filter=True
            )


    def parse_speaker(self, response: Response):

        output: dict[str, dict | list] = {
            "info_speaker": {},
            "sessions": [],
        }

        output['info_speaker'] = self._get_info_speaker(response)
    
        sessions = response.xpath(SessionXpath.ALL_SESSIONS.value)
        if not sessions:
            return None
        
        for index, session in enumerate(sessions):
            session_data = self._extract_session_data(session)
            if not session_data:
                # self.logger.warning(f"No session data found for session at index {index}")
                continue
            output['sessions'].append(session_data)

        yield from self._save_info(output)


    def _save_info(self, output_speaker: dict[str, dict | list]):
        speaker_info = output_speaker['info_speaker']
        
        if not output_speaker['sessions']:
            item = TheDistrictShowItem()
            item['name_speaker'] = speaker_info['name']
            item['image_speaker'] = speaker_info['image']
            item['linkedin_speaker'] = speaker_info['linkedin']
            item['whatsapp_speaker'] = speaker_info['whatsapp']
            item['X_speaker'] = speaker_info['X']
            item['company'] = speaker_info['position']
            item['company_position_speaker'] = speaker_info['company']
            item['description_speaker'] = speaker_info['description']
            item['date_session'] = ''
            item['address'] = ''
            item['name_session'] = ''
            item['source_speaker_url'] = speaker_info['source_speaker_url']
            yield item
        else:
            for session in output_speaker['sessions']:
                item = TheDistrictShowItem()
                item['name_speaker'] = speaker_info['name']
                item['image_speaker'] = speaker_info['image']
                item['linkedin_speaker'] = speaker_info['linkedin']
                item['whatsapp_speaker'] = speaker_info['whatsapp']
                item['X_speaker'] = speaker_info['X']
                item['company'] = speaker_info['position']
                item['company_position_speaker'] = speaker_info['company']
                item['description_speaker'] = speaker_info['description']
                item['date_session'] = session.get('date_session') or ''
                item['address'] = session.get('address') or ''
                item['name_session'] = session.get('name_session') or ''
                item['source_speaker_url'] = speaker_info['source_speaker_url']
                yield item

    def _extract_session_data(self, response_session: Selector) -> dict:

        try:
            session_div = response_session.xpath(
                SessionXpath.CONTAINER.value
            )

            if not session_div:
                # print("No session div found")
                return {}
            
            session_div = session_div[0]
            date = session_div.xpath(SessionXpath.DATE.value).get()
            time = session_div.xpath(SessionXpath.TIME.value).get()
            address = session_div.xpath(SessionXpath.ADDRESS.value).get()
            name_session = session_div.xpath(SessionXpath.NAME.value).get()

            date_session = (
                f"{date.strip()} | {time.strip()}" if date and time else ''
            ).strip()

            return {
                "date_session": date_session,
                "address": (address.strip() if address else '').strip(),
                "name_session": (name_session.strip() if name_session else '').strip(),
            }

        except Exception as exc:
            print(f"[extract_session_data] Error parsing session data: {exc}")
            return {}


    def _get_info_speaker(self, response: Selector):

        output = {
            "name": (response.xpath(ConfigXpath.SPEAKER_NAME.value).get() or '').strip(),
            "image": (self._get_image(response, response.xpath(ConfigXpath.SPEAKER_NAME.value).get()) or '').strip(),
            "linkedin": (response.xpath(ConfigXpath.URL_LINKEDIN.value).get() or '').strip(),
            "whatsapp": (response.xpath(ConfigXpath.URL_WHATSAPP.value).get() or '').strip(),
            "X": (response.xpath(ConfigXpath.URL_X.value).get() or '').strip(),
            "position": (response.xpath(ConfigXpath.COMPANY_INFO.value).xpath(ConfigXpath.POSITION.value).get() or '').strip(),
            "company": (response.xpath(ConfigXpath.COMPANY_INFO.value).xpath(ConfigXpath.COMPANY.value).get() or '').strip(),
            "description": (response.xpath(ConfigXpath.DESCRIPTION.value).get() or '').strip(),
            "source_speaker_url": response.url,
        }
        return output



    def _get_image(self, response: Selector, name_speaker: None | str):
        if name_speaker is None:
            return ''

        image_xpath = f'//img[@alt="{name_speaker}"]/@src'
        image = response.xpath(image_xpath).get()

        if image is None:
            return ''

        return image