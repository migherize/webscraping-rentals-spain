import re
import logging
from enum import Enum
from scrapingbee import ScrapingBeeClient
from app.models.enums import ScrapingBeeParams
from app.scrapy.flipcoliving.pipeline import (
    byte_string_to_dict,
    refine_extractor_data,
    save_data,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class XpathParseData(Enum):
    LANGUAGE_URL = {
        "selector": '//div[contains(@class, "languageDropdown")]//a/@href',
        "type": "list",
        "clean": True,
    }

    CITIES_URL = {
        "selector": '//ul[contains(@id, "menu-locations-menu-1")]//@href',
        "type": "list",
        "clean": True,
    }

    COLIVING_URL = {
        "selector": "//a[contains(@class, 'card__textBottom')]//@href",
        "type": "list",
        "clean": True,
    }

    SPACE_IMAGENES = {
        "selector": (
            "//div[contains(@class, 'carouselBanner__imageWrap slide')]//img/@src | "
            "//div[contains(@class, 'carouselBanner__imageWrap slide')]//img/@data-flickity-lazyload-src | "
            "//div[contains(@class, 'carouselBanner__imageWrap slide')]//img/@srcset"
        ),
        "type": "list",
        "clean": True,
    }

    THE_UNIT = {
        "selector": (
            "//div[contains(@class, 'plotHasHoverEffect card__modalTrigger')]//img/@src | "
            "//div[contains(@class, 'plotHasHoverEffect card__modalTrigger')]//img/@data-flickity-lazyload-src | "
            "//div[contains(@class, 'plotHasHoverEffect card__modalTrigger')]//img/@srcset"
        ),
        "type": "list",
        "clean": True,
    }

    THE_FLOOR_PLAN = {
        "selector": (
            "//div[contains(@class, 'floorPlan__imageWrap')]//img/@src | "
            "//div[contains(@class, 'floorPlan__imageWrap')]//img/@data-flickity-lazyload-src | "
            "//div[contains(@class, 'floorPlan__imageWrap')]//img/@srcset"
        ),
        "type": "list",
        "clean": True,
    }

    COLIVING_NAME = {
        "selector": "//h2[contains(@class, 'carouselBanner__title')]",
    }
    BANNER_FEATURES = {
        "selector": "//ul[contains(@class, 'carouselBanner__features')]//li",
        "type": "list",
        "clean": True,
    }
    ABOUT_THE_HOME = {
        "selector": "//div[contains(@class, 'sectionIntro__text')]//p",
    }
    FEATURE = {
        "selector": "//span[contains(@class, 'homesFeatures__text')]",
        "type": "list",
        "clean": True,
    }
    NEIGHBORHOOD_DESCRIPTION = {
        "selector": "//div[contains(@class, 'localAreaMap__imageText')]//p",
    }
    BATHROOM_SQUARE_METERS = {
        "selector": "//div[contains(@class, 'card__features')]/span",
        "type": "list",
        "clean": True,
    }
    AVAILABLE = {
        "selector": "//span[contains(@class, 'card__label')]//text()",
        "clean": True,
    }
    LATITUDE = {
        "selector": "//div[contains(@class, 'localAreaMap__half localAreaMap__map mapboxgl-map')]//@data-lng"
    }
    LONGITUDE = {
        "selector": "//div[contains(@class, 'localAreaMap__half localAreaMap__map mapboxgl-map')]//@data-lat"
    }
    TOUR_URL = {
        "selector": "//iframe[contains(@src, 'matterport')]/@src",
        "clean": True,
    }



def get_information_response(
    client: ScrapingBeeClient, url: str, extract_rules: dict
) -> dict:
    """
    Retrieves information from a specified URL using ScrapingBee and extract rules.

    Args:
        client (ScrapingBeeClient): The ScrapingBee client instance.
        url (str): The URL from which to extract information.
        extract_rules (dict): A dictionary defining extraction rules for the desired data.

    Returns:
        dict: A dictionary containing the extracted data.

    Raises:
        Exception: If there is an issue with the request or data extraction.
    """
    try:
        response = client.get(
            url,
            params={
                ScrapingBeeParams.RENDER_JS.value: "true",
                ScrapingBeeParams.EXTRACT_RULES.value: extract_rules,
            },
        )

        if response.status_code != 200:
            logger.error(
                "Failed to retrieve data: Status code %s", response.status_code
            )
            return {"error": f"Error: Status code {response.status_code}"}

        results = response.content
        results_dict = byte_string_to_dict(
            results
        )  # Assuming this function is defined elsewhere
        return results_dict

    except Exception as e:
        logger.exception("An error occurred while getting information response")
        raise e


def scrape_flipcoliving(api_key: str, url: str) -> dict:
    """
    Scrapes the FlipColiving website for city URLs using the ScrapingBee API.

    Args:
        api_key (str): The API key for accessing ScrapingBee.
        url (str): The base URL of the FlipColiving website.

    Returns:
        dict: A dictionary containing the city URLs and other metadata.

    Raises:
        Exception: If there is an issue with the scraping process.
    """
    try:
        client = ScrapingBeeClient(api_key=api_key)
        response = client.get(url=url)

        # Extract city URLs from the response
        data = get_information_response(
            client,
            response.url,
            {
                "cities_url": XpathParseData.CITIES_URL.value,
            },
        )

        if isinstance(data, str):
            logger.error("Failed to scrape data: %s", data)
            return {"error": data}

        # Normalize city URLs
        data["cities_url"] = [url + new_url for new_url in data["cities_url"]]

        meta = {"base_url": url}

        for _, city_url in enumerate(data["cities_url"]):
            city_name = re.sub(r"[^A-Za-z]", " ", city_url.split("-")[-1]).strip()
            meta["city_name"] = city_name
            meta["city_url"] = city_url

            logger.info("Parsing coliving data for %s at %s", city_name, city_url)
            parse_all_coliving(client=client, city_url=city_url, meta=meta)
            break

    except Exception as e:
        logger.exception("An error occurred during scraping")
        raise e


def parse_all_coliving(
    client: ScrapingBeeClient,
    city_url: str,
    meta: dict,
) -> None:
    """
    Parses all coliving spaces from a given city URL.

    Args:
        client (ScrapingBeeClient): The ScrapingBee client used to perform requests.
        city_url (str): The URL of the city to scrape coliving spaces from.
        meta (dict): A dictionary containing metadata to pass to the parsing function.

    Returns:
        None: This function does not return a value but processes coliving URLs.
    """
    try:
        response = client.get(url=city_url)

        # Extract coliving URLs
        data = get_information_response(
            client,
            response.url,
            {
                "coliving_url": XpathParseData.COLIVING_URL.value,
            },
        )

        if isinstance(data, str):
            logger.error("Failed to extract data: %s", data)
            return

        for coliving_url in data.get("coliving_url", []):
            meta["coliving_url"] = coliving_url
            parse_coliving(client=client, coliving_url=coliving_url, meta=meta)
            break

    except Exception as e:
        logger.error(
            "Error while parsing coliving spaces for city URL %s: %s", city_url, e
        )


def parse_coliving(
    client: ScrapingBeeClient,
    coliving_url: str,
    meta: dict,
) -> None:
    """
    Parses information about a coliving space from a given coliving URL.

    Args:
        client (ScrapingBeeClient): The ScrapingBee client used to perform requests.
        coliving_url (str): The URL of the coliving space to scrape.
        meta (dict): A dictionary containing metadata related to the coliving space.

    Returns:
        None: This function does not return a value but processes coliving information and appends it to a CSV file.
    """
    try:
        response = client.get(url=coliving_url)

        # Extracting information from the coliving page
        data = get_information_response(
            client,
            response.url,
            {
                "space_images": XpathParseData.SPACE_IMAGENES.value,
                "coliving_name": XpathParseData.COLIVING_NAME.value,
                "Banner__features": XpathParseData.BANNER_FEATURES.value,
                "about_the_home": XpathParseData.ABOUT_THE_HOME.value,
                "features": XpathParseData.FEATURE.value,
                "neighborhood_description": XpathParseData.BATHROOM_SQUARE_METERS.value,
                "bathroom_square_meters": XpathParseData.BATHROOM_SQUARE_METERS.value,
                "the_unit": XpathParseData.THE_UNIT.value,
                "the_floor_plan": XpathParseData.THE_FLOOR_PLAN.value,
                "available": XpathParseData.AVAILABLE.value,
                "latitude": XpathParseData.LATITUDE.value,
                "longitude": XpathParseData.LONGITUDE.value,
                "tour_url": XpathParseData.TOUR_URL.value,
            },
        )

        if isinstance(data, str):
            logger.error("Failed to extract data: %s", data)
            return
        # Extracting information from the coliving page to decription
        data_language = get_information_response(
            client,
            response.url,
            {
                "language_url": XpathParseData.LANGUAGE_URL.value,
            },
        )

        if isinstance(data, str):
            logger.error("Failed to extract data: %s", data)
            return

        items_description_with_language_code = {
            index_language: [
                url,
                get_information_response(
                    client,
                    url,
                    {
                        "about_the_home": XpathParseData.ABOUT_THE_HOME.value,
                    },
                ),
            ]
            for index_language, url in enumerate(data_language["language_url"])
        }
        data["city_name"] = meta["city_name"]
        data["referenceCode"] = f'{data["city_name"]}-{data["coliving_name"]}-0001'

        data = refine_extractor_data(data, items_description_with_language_code)
        save_data(data)

    except Exception as e:
        logger.error(
            "Error while parsing coliving data from URL %s: %s", coliving_url, e
        )


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    url = os.getenv("FLIPCOLIVING_URL")
    api_key = os.getenv("SCRAPINGBEE_API_KEY")
    url_test = os.getenv("URL_TEST")

    client = ScrapingBeeClient(api_key=api_key)

    parse_coliving(
        client=client,
        coliving_url=url_test,
        meta={
            "city_name": "Madrid",
        },
    )
