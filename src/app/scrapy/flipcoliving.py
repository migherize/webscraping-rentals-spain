import os
import re
import ast
import json
import logging
import calendar
from enum import Enum
from datetime import datetime
from scrapingbee import ScrapingBeeClient
from app.models.enums import ScrapingBeeParams, feature_map
from app.models.schemas import Description, LocationAddress, Property
from app.utils.funcs import find_feature_keys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class RegexPatterns(str, Enum):
    RATE = r"[\d,.]+€"
    BEDROOMS = r"habitaciones|bedrooms"
    AREA_SQM = r"[Mm]2|[Ss][Qq][Mm]"
    NON_DIGITS = r"[^\d.,]+"


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


def remove_duplicate_urls(url_list: list) -> list:
    cleaned_urls = []

    for url in url_list:
        clean_url = re.sub(r"-\d+x\d+\.jpg", ".jpg", url.split()[0])
        cleaned_urls.append(clean_url)

    return list(set(cleaned_urls))


def get_month_dates(text: str) -> tuple:
    """
    Extracts the month and year from a string and returns the start and end 
    dates of the corresponding month in the "%Y-%m-%d" format.
    
    If the month is misspelled or the format is incorrect,
    it issues a warning and returns (None, None).
    
    Parameters:
    text (str): String in the format "Available from <Month> <Year>".
    
    Returns:
    tuple: Start and end dates of the month as strings in "%Y-%m-%d" format,
           or (None, None) if there is an error in the input.
    """
    
    try:
        # Extract month and year from the text
        date_str = text.replace('Available from ', '')
        date_obj = datetime.strptime(date_str, '%B %Y')

        # Get the last day of the month
        _, last_day = calendar.monthrange(date_obj.year, date_obj.month)

        # Create the start and end dates
        start_date = date_obj.replace(day=1).strftime('%Y-%m-%d')
        end_date = date_obj.replace(day=last_day).strftime('%Y-%m-%d')

        return start_date, end_date
    
    except ValueError:
        # Handle the case where the month or format is incorrect
        logger.error("Warning: The month or input format '%s' is incorrect.", text)
        return None, None


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


def byte_string_to_dict(byte_string: bytes) -> dict:
    """
    Converts a byte string containing a Python-like dictionary to a valid JSON object.

    Args:
        byte_string (bytes): A byte string that represents a dictionary in Python format.

    Returns:
        dict: A dictionary representation of the byte string.

    Raises:
        ValueError: If the byte string cannot be decoded or evaluated.
    """
    try:
        decoded_string = byte_string.decode("utf-8")
        python_dict = ast.literal_eval(decoded_string)

        if not isinstance(python_dict, dict):
            raise ValueError("Decoded string does not represent a valid dictionary.")

        return python_dict

    except (UnicodeDecodeError, ValueError, SyntaxError) as e:
        logger.error("Failed to convert byte string to dictionary: %s", e)
        raise ValueError(f"Invalid byte string provided: {str(e)}")


def extract_features(all_data: list):
    neighborhood = all_data[0]
    rate_min = ""
    rate_max = ""
    area_sqm = ""
    bedrooms = ""

    for data in all_data:
        if re.findall(RegexPatterns.RATE.value, data):
            rates = re.findall(RegexPatterns.RATE.value, data)
            print("rates:", rates)
            rate_min, rate_max = rates

        if re.search(RegexPatterns.BEDROOMS.value, data):
            bedrooms = re.sub(RegexPatterns.NON_DIGITS.value, "", data).strip()

        if re.search(RegexPatterns.AREA_SQM.value, data):
            area_sqm = re.sub(RegexPatterns.AREA_SQM.value, "", data).strip()

    return neighborhood, rate_min, rate_max, area_sqm, bedrooms


def refine_extractor_data(
    data: dict, items_description_with_language_code: dict
) -> dict:
    data["space_images"] = remove_duplicate_urls(data["space_images"])
    data["the_unit"] = remove_duplicate_urls(data["the_unit"])
    data["the_floor_plan"] = remove_duplicate_urls(data["the_floor_plan"])
    data["features"] = find_feature_keys(data["features"], feature_map)

    neighborhood, min_price, max_price, area_sqm, bedrooms = extract_features(
        data["Banner__features"]
    )

    data["neighborhood"] = neighborhood
    data["min_price"] = min_price
    data["max_price"] = max_price
    data["area_sqm"] = area_sqm
    data["bedrooms"] = bedrooms
    data["bathroom_square_meters"] = (
        data["bathroom_square_meters"][1]
        if len(data["bathroom_square_meters"]) > 1
        else None
    )

    # TODO: Placeholder for additional data
    data["take_a_tour"] = ""

    data["Descriptions"] = get_all_descriptions(items_description_with_language_code)

    return data


def get_all_descriptions(items_description_with_language_code: dict):
    all_descriptions = []
    for id_language, info_description in items_description_with_language_code.items():
        info_description: list
        # url_language = info_description[0]
        descriptions = {
            "LanguagesId": "",
            "title": "",
            "description": "",
        }
        descriptions["LanguagesId"] = id_language

        try:
            descriptions["description"] = info_description[1]["about_the_home"]
        except:
            pass

        if descriptions["description"] == "":
            continue

        all_descriptions.append(descriptions)

    return all_descriptions


def get_default_values() -> dict:
    """
    Retorna un diccionario con los valores por defecto (hardcoded).
    """
    return {
        "cancellationPolicy": "standard",
        "rentalType": "individual",
        "isActive": True,
        "isPublished": True,
        "Languages": [1, 2],
        "videoUrl": "",
        "tourUrl": "",
        "PropertyTypeId": 4, # Coliving
        "Images": [
            {
                "image": "https://lodgerin-archives-production.s3.amazonaws.com/uploads/archive/name/34564/10.jpg",
                "isCover": True,
            },
            {
                "image": "https://lodgerin-archives-production.s3.amazonaws.com/uploads/archive/name/34564/10.jpg",
                "isCover": False,
            },
            {
                "image": "https://lodgerin-archives-production.s3.amazonaws.com/uploads/archive/name/34564/10.jpg",
                "isCover": False,
            },
        ],
        "country": "Spain",
        "countryCode": "ES",
    }


def save_data(data: dict, id_coliving: str) -> Property:

    defaults = get_default_values()

    item = Property(
        name=data["coliving_name"],
        description=data["Descriptions"][0]["description"],
        referenceCode=id_coliving,
        areaM2=data["area_sqm"],
        rentalType=defaults["rentalType"],
        isActive=defaults["isActive"],
        isPublished=defaults["isPublished"],
        Features=data["features"],
        videoUrl=defaults["videoUrl"],
        tourUrl=defaults["tourUrl"],
        PropertyTypeId=defaults["PropertyTypeId"],
        Descriptions=[
            Description(
                LanguagesId=data_description["LanguagesId"],
                title=data_description["title"],
                description=data_description["description"],
            ).dict()
            for data_description in data["Descriptions"]
        ],
        Images=defaults["Images"],
        Location=LocationAddress(
            lat=data["latitude"],
            lon=data["longitude"],
            country=defaults["country"],
            countryCode=defaults["countryCode"],
            city=data["city_name"],
        ),
    )

    return item


def create_json(item: Property) -> None:
    class PathDocument(Enum):
        PATH_DOCUMENT = "data"
        DOCUMENT_JS = "output_document.json"

    current_dir = os.getcwd()
    json_file_path = os.path.join(
        current_dir, PathDocument.PATH_DOCUMENT.value, PathDocument.DOCUMENT_JS.value
    )
    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)

    with open(json_file_path, "a", encoding="utf-8-sig") as json_file:
        json.dump(item.dict(), json_file, indent=4)

    print(f"Datos guardados en: {json_file_path}")


#TODO: split Webscraping
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

        for index, city_url in enumerate(data["cities_url"]):
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
        id_coliving = id_coliving = f'{data["city_name"]}-{data["coliving_name"]}-0001'

        data = refine_extractor_data(data, items_description_with_language_code)
        item = save_data(data, id_coliving)
        # Rentail
        create_json(item)

    except Exception as e:
        logger.error(
            "Error while parsing coliving data from URL %s: %s", coliving_url, e
        )


if __name__ == "__main__":
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
