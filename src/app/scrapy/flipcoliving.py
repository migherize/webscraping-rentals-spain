import os
import re
import ast
import json
import pandas as pd
import logging
from enum import Enum
from scrapingbee import ScrapingBeeClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScrapinBeeParams(str, Enum):
    RENDER_JS = "render_js"
    EXTRACT_RULES = "extract_rules"

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
                ScrapinBeeParams.RENDER_JS.value: "true",
                ScrapinBeeParams.EXTRACT_RULES.value: extract_rules,
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
                "cities_url": {
                    "selector": '//ul[contains(@id, "menu-locations-menu-1")]//@href',
                    "type": "list",
                    "clean": True,
                },
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
                "coliving_url": {
                    "selector": "//a[contains(@class, 'card__textBottom')]//@href",
                    "type": "list",
                    "clean": True,
                },
            },
        )

        if isinstance(data, str):
            logger.error("Failed to extract data: %s", data)
            return

        for coliving_url in data.get("coliving_url", []):
            meta["coliving_url"] = coliving_url
            parse_coliving(client=client, coliving_url=coliving_url, meta=meta)

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
                "space_images": {
                    "selector": "//a[contains(@class, 'plotHasHoverEffect')]//img",
                    "type": "list",
                    "clean": True,
                },
                "coliving_name": {
                    "selector": "//h2[contains(@class, 'carouselBanner__title')]",
                },
                "Banner__features": {
                    "selector": "//ul[contains(@class, 'carouselBanner__features')]//li",
                    "type": "list",
                    "clean": True,
                },
                "about_the_home": {
                    "selector": "//div[contains(@class, 'sectionIntro__text')]//p",
                },
                "features": {
                    "selector": "//span[contains(@class, 'homesFeatures__text')]",
                    "type": "list",
                    "clean": True,
                },
                "neighborhood_description": {
                    "selector": "//div[contains(@class, 'localAreaMap__imageText')]//p",
                },
                "bathroom_square_meters": {
                    "selector": "//div[contains(@class, 'card__features')]/span",
                    "type": "list",
                    "clean": True,
                },
            },
        )

        if isinstance(data, str):
            logger.error("Failed to extract data: %s", data)
            return

        for key, value in data.items():
            logger.info("%s -> %s", key, value)

        (neighborhood, min_price, max_price, area_sqm, bedrooms) = (
            extract_features(
                data["Banner__features"]
            )
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

        #TODO: Placeholder for additional data
        data["the_unit"] = ""
        data["Available"] = ""
        data["the_floor_plan"] = ""
        data["take_a_tour"] = ""

        json_file_path = os.path.join(
                "/app/data/", 
                "items.json"
            )
            
        with open(json_file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

    except Exception as e:
        logger.error(
            "Error while parsing coliving data from URL %s: %s", coliving_url, e
        )


def extract_features(all_data: list):
    neighborhood = all_data[0]
    precio_min = ""
    precio_max = ""
    area_sqm = ""
    bedrooms = ""

    # TODO: Revisar

    return neighborhood, precio_min, precio_max, area_sqm, bedrooms


def main():
    """
    Función principal para iniciar el scraping.
    """
    from dotenv import load_dotenv
    load_dotenv()

    url = "XSU4FUMILTDH4LMC46PTNI8B3YLXIV0CFM32KAMCMDRTTJJEENHC6G1PYBZAKY77P16RCBV5567Y8550"
    api_key = "https://flipcoliving.com/"

    scraped_data = scrape_flipcoliving(api_key, url)
    
    json_file_path = os.path.join(
        "/data/", 
        "output_document.json"
    )
    
    with open(json_file_path, 'w') as json_file:
        json.dump(scraped_data, json_file, indent=4)

if __name__ == "__main__":
    main()
