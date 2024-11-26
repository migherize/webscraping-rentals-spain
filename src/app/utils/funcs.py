import re
import os
import logging
from datetime import datetime, timedelta
from app.models.enums import (
    Month,
    PropertyType,
    ContractModels,
    CurrencyCode,
    Languages,
)
from app.utils.lodgerinService import LodgerinAPI
import app.utils.constants as constants
from app.models.schemas import DatePayloadItem

os.makedirs(constants.LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            os.path.join(constants.LOG_DIR, "app.log"), mode="a", encoding="utf-8"
        ),
    ],
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def detect_language(description: str) -> int:
    spanish_keywords = [
        " es ",
        " de ",
        " la ",
        " el ",
        " y ",
        " en ",
        "un ",
        "una ",
        "los ",
        "las ",
    ]
    english_keywords = [" is ", " the ", " a ", " an ", " and ", " in ", "to ", "of "]

    spanish_count = sum(description.lower().count(word) for word in spanish_keywords)
    english_count = sum(description.lower().count(word) for word in english_keywords)

    if spanish_count > english_count:
        return Languages.SPANISH.value
    elif english_count > spanish_count:
        return Languages.ENGLISH.value
    else:
        return None


def get_currency_code(symbol: str) -> str:
    """
    Función para obtener el acrónimo de la moneda dado un símbolo.

    Args:
        symbol (str): Símbolo de la moneda (ejemplo: $, €, etc.).

    Returns:
        str: Acrónimo de la moneda correspondiente, o None si no se encuentra.
    """
    symbol_to_code = {
        "$": CurrencyCode.USD.value,
        "CAD": CurrencyCode.CAD.value,
        "€": CurrencyCode.EUR.value,
        "ZWL": CurrencyCode.ZWL.value,
    }

    return symbol_to_code.get(symbol, None)


def get_month_dates(text: str):
    regex = (
        r"(now|january|february|march|april|may|june|july|august|september|october|november|december|"
        r"enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)"
    )

    match = re.search(regex, text, re.IGNORECASE)

    if match:
        month_name = match.group(1).lower()
        current_date = datetime.now()
        start_date = current_date.strftime("%Y-%m-%d")

        if month_name == "now":
            # "Now" case - return the current month's start and end dates
            month = current_date.month
            year = current_date.year
        else:
            try:
                month_enum = Month[month_name.upper()]
                month = month_enum.value
            except KeyError:
                return None, None

            year = (
                current_date.year
                if month >= current_date.month
                else current_date.year + 1
            )

        # Calculate end date for the selected month and year
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)

        return start_date, end_date.strftime("%Y-%m-%d")
    else:
        return None, None


def find_feature_keys(features_list: str, feature_map: dict):
    features_text = ", ".join(features_list)
    text = features_text.lower()
    matched_features = []
    for feature_key, terms in feature_map.items():
        for term in terms:
            if re.search(
                r"(?<!\bnot\b\s)(?<!\bno\b\s)\b" + re.escape(term) + r"\b", text
            ):
                matched_features.append(feature_key)
                break

    return matched_features


def get_elements_types(term, elements):
    if elements:
        contract_types = elements.get("data", [])

        for contract_type in contract_types:
            if contract_type.get("name") == term:
                return contract_type.get("id")
        return None
    else:
        return None


def save_property(property_item, api_key):
    property_dict = property_item.model_dump()
    lodgerin_api = LodgerinAPI(api_key)
    response = lodgerin_api.create_or_update_property(property_dict)

    if response is not None and "msg" in response and "data" in response:
        if response["msg"] == "The property has been saved successfully!":
            data = response["data"]
            logger.info(
                f"Property saved successfully! Property Code: {data.get('code')}, Property ID: {data.get('id')}, Property Name: {data.get('name')}"
            )
            return data.get("id")
        else:
            logger.info(f"Unexpected message: {response['msg']}")
    else:
        logger.info("Failed to save property. No valid response received.")
    return None


def save_rental_unit(rental_unit_item, api_key):
    rental_unit_dict = rental_unit_item.model_dump()
    lodgerin_api = LodgerinAPI(api_key)
    response = lodgerin_api.create_or_update_rental_unit(rental_unit_dict)

    if response is not None and "msg" in response and "data" in response:
        if response["msg"] == "The rental unit has been saved successfully!":
            data = response["data"]
            logger.info(
                f"rental_unit saved successfully! rental_unit ID: {data.get('id')}"
            )
            return data.get("id")
        else:
            logger.info(f"Unexpected message: {response['msg']}")
    else:
        logger.info("Failed to save rental_unit. No valid response received.")
    return None


def check_and_insert_rental_unit_calendar(
    rental_unit_id: str, calendar_unit: DatePayloadItem, api_key:str
):
    lodgerin_api = LodgerinAPI(api_key)
    dates_payload = [calendar_unit.model_dump()]

    try:
        existing_schedule = lodgerin_api.get_rental_unit_calendar(rental_unit_id)
        logger.info("existing_schedule",existing_schedule)

        if existing_schedule is None or not existing_schedule.get("data"):
            logger.info(f"Inserting new dates for rental unit ID {rental_unit_id}")
            response = lodgerin_api.create_rental_unit_calendar(
                rental_unit_id, dates_payload
            )
            if response:
                logger.info(
                    f"Successfully inserted dates for rental unit ID {rental_unit_id}"
                )
            else:
                logger.info(
                    f"Error inserting dates for rental unit ID {rental_unit_id}"
                )

        else:
            existing_end_dates = {
                event["endDate"] for event in existing_schedule["data"]
            }
            exists = any(
                payload["endDate"] in existing_end_dates for payload in dates_payload
            )
            if exists:
                logger.info(
                    f"Rental unit ID {rental_unit_id} already has the correct end date."
                )

            else:
                logger.info(f"Updating end date for rental unit ID {rental_unit_id}")
                response = lodgerin_api.create_rental_unit_calendar(
                    rental_unit_id, dates_payload
                )
                if response:
                    logger.info(
                        f"Successfully updated end date for rental unit ID {rental_unit_id}"
                    )
                else:
                    logger.info(
                        f"Error updating end date for rental unit ID {rental_unit_id}"
                    )

    except Exception as e:
        logger.info(f"An error occurred for rental unit ID {rental_unit_id}: {e}")


def remove_html(text):
    """
    Removes all HTML tags and characters from a string.

    Args:
        text (str): The string containing HTML tags.

    Returns:
        str: The cleaned string, without HTML tags.
    """
    cleaned_text = re.sub(r"<.*?>", "", text)
    return cleaned_text


def clean_image_urls(image_string):
    """
    Cleans a string containing image URLs and returns a list of cleaned URLs.

    Args:
        image_string (str): The string containing image URLs, separated by commas.

    Returns:
        list: A list of cleaned image URLs.
    """
    cleaned_string = image_string.replace("\\/", "/")
    url_list = cleaned_string.split(",")
    return url_list
