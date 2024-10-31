import re
import logging
from datetime import datetime, timedelta
from app.models.enums import Month, PropertyType, ContractModels
from app.utils.lodgerinService import LodgerinAPI
import app.utils.constants as constants
from app.models.schemas import DatePayloadItem

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log", mode="a", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def get_month_dates(text):
    regex = (
        r"(january|february|march|april|may|june|july|august|september|october|november|december|"
        r"enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)"
    )

    match = re.search(regex, text, re.IGNORECASE)

    if match:
        month_name = match.group(1).lower()
        current_date = datetime.now()
        start_date = current_date.strftime("%Y-%m-%d")

        try:
            month_enum = Month[month_name.upper()]
        except KeyError:
            return None, None

        month = month_enum.value

        current_year = current_date.year
        current_month = current_date.month
        year = current_year if month >= current_month else current_year + 1

        if month == 1:
            end_date = datetime(year - 1, 12, 31)
        else:
            end_date = datetime(year, month - 1, 1) + timedelta(days=-1)

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


def get_elements_types(term):
    lodgerin_api = LodgerinAPI(constants.LODGERIN_API_KEY)

    if term in {ptype.value for ptype in PropertyType}:
        elements = lodgerin_api.get_property_types()

    elif term in {ptype.value for ptype in ContractModels}:
        elements = lodgerin_api.get_elements()

    else:
        return None

    if elements:
        contract_types = elements.get("data", [])

        for contract_type in contract_types:
            if contract_type.get("name") == term:
                return contract_type.get("id")
        return None
    else:
        return None


def save_property(property_item):
    property_dict = property_item.model_dump()
    lodgerin_api = LodgerinAPI(constants.LODGERIN_API_KEY)
    response = lodgerin_api.create_or_update_property(property_dict)

    if response is not None and "msg" in response and "data" in response:
        if response["msg"] == "The property has been saved successfully!":
            data = response["data"]
            logger.info(f"Property saved successfully! Property Code: {data.get('code')}, Property ID: {data.get('id')}, Property Name: {data.get('name')}")
            return data.get("id")
        else:
            logger.info(f"Unexpected message: {response['msg']}")
    else:
        logger.info("Failed to save property. No valid response received.")
    return None


def save_rental_unit(rental_unit_item):
    rental_unit_dict = rental_unit_item.model_dump()
    lodgerin_api = LodgerinAPI(constants.LODGERIN_API_KEY)
    response = lodgerin_api.create_or_update_rental_unit(rental_unit_dict)

    if response is not None and "msg" in response and "data" in response:
        if response["msg"] == "The rental unit has been saved successfully!":
            data = response["data"]
            logger.info(f"rental_unit saved successfully! rental_unit ID: {data.get('id')}")
            return data.get("id")
        else:
            logger.info(f"Unexpected message: {response['msg']}")
    else:
        logger.info("Failed to save rental_unit. No valid response received.")
    return None


def check_and_insert_rental_unit_calendar(
    rental_unit_id: str, calendar_unit: DatePayloadItem
):
    lodgerin_api = LodgerinAPI(constants.LODGERIN_API_KEY)
    dates_payload = [calendar_unit.model_dump()]

    try:
        existing_schedule = lodgerin_api.get_rental_unit_calendar(rental_unit_id)
        logger.info(existing_schedule)

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
