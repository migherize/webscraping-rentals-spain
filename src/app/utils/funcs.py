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


[
    {
        "space_images": [
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-001-2700x1200.jpg",
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-001-380x253.jpg 380w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-001-760x507.jpg 760w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-001-1140x760.jpg 1140w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-001-1200x800.jpg 1400w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-001-2400x1600.jpg 2800w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-001-3600x2400.jpg 4200w",
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-003-2700x1200.jpg",
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-003-380x253.jpg 380w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-003-760x507.jpg 760w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-003-1140x760.jpg 1140w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-003-1200x800.jpg 1400w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-003-2400x1600.jpg 2800w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-003-3600x2400.jpg 4200w",
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-002-2700x1200.jpg",
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-002-380x253.jpg 380w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-002-760x507.jpg 760w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-002-1140x760.jpg 1140w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-002-1200x800.jpg 1400w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-002-2400x1600.jpg 2800w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-002-3600x2400.jpg 4200w",
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W004.jpg",
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W004-380x253.jpg 380w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W004-760x507.jpg 760w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W004-1140x760.jpg 1140w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W004-1200x800.jpg 1400w",
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W010.jpg",
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W010-380x253.jpg 380w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W010-760x507.jpg 760w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W010-1140x760.jpg 1140w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W010-1200x800.jpg 1400w",
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W009.jpg",
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W009-380x253.jpg 380w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W009-760x507.jpg 760w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W009-1140x760.jpg 1140w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W009-1200x800.jpg 1400w",
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W011.jpg",
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W011-380x253.jpg 380w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W011-760x507.jpg 760w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W011-1140x760.jpg 1140w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W011-1200x800.jpg 1400w",
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W012.jpg",
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W012-380x253.jpg 380w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W012-760x507.jpg 760w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W012-1140x760.jpg 1140w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W012-1200x800.jpg 1400w",
        ],
        "coliving_name": "Cantueso",
        "Banner__features": [
            "Valdeacederas",
            "From 795€ to 1100€ /month",
            "500 sqm",
            "20 bedrooms",
        ],
        "about_the_home": "Cantueso is an exceptional twenty-bedroom guesthouse with an extraordinary curation of decoration and art. Live the Madrid dream in this stunning guesthouse that oozes elegance and peace. The rich décor and high ceilings are particularly spectacular, and the huge kitchen on the upper floor provides a contrast to the more formal ambience of the living and dining areas. The guesthouse has a terrace for unwinding after a day in the city.",
        "features": [
            "Blazing fast Wi-Fi",
            "On-Site laundry",
            "Fully equipped kitchen",
            "Linens",
            "Coffee machine",
            "Dishwasher",
            "Washer",
            "Dryer",
            "Hot and cold A/C",
            "Amazing shared spaces",
            "Smart TV",
            "Iron",
            "Bathroom",
            "Hangers",
            "Keyless access",
            "Non smoking",
            "Access exclusive events",
            "Close to metro station",
            "Close to bus station",
            "Bicycle parking",
            "Oven",
            "Fridge",
            "BBQ / Grill",
            "Towels",
            "Private bedroom",
            "Fitness center",
            "Guesthouse",
            "Coworking",
            "Private desk",
            "Shared areas daily cleaning",
            "Quick repairs service",
            "Fully furnished",
            "No pets allowed",
            "Couples are allowed",
        ],
        "bathroom_square_meters": ["From 795€ to 1100€ /month", "12 sqm", ""],
        "titles_rental_units": [],
        "the_unit": [
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W006-900x720.jpg",
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W006-380x253.jpg 380w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W006-760x507.jpg 760w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W006-1140x760.jpg 1140w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W006-1200x800.jpg 1400w",
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W005-900x720.jpg",
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W005-380x253.jpg 380w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W005-760x507.jpg 760w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W005-1140x760.jpg 1140w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W005-1200x800.jpg 1400w",
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W007-900x720.jpg",
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W007-380x253.jpg 380w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W007-760x507.jpg 760w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W007-1140x760.jpg 1140w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W007-1200x800.jpg 1400w",
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W008-900x720.jpg",
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W008-380x570.jpg 380w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W008-760x1140.jpg 760w, https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W008-534x800.jpg 1400w",
        ],
        "the_floor_plan": [
            "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 2509 2273'%3E%3C/svg%3E",
            "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1649 2560'%3E%3C/svg%3E",
            "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1623 2560'%3E%3C/svg%3E",
            "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1487 2560'%3E%3C/svg%3E",
            "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1646 2560'%3E%3C/svg%3E",
        ],
        "available": ["Available from December"],
        "latitude": "-3.7056482",
        "longitude": "40.4670626",
        "tour_url": [
            "https://my.matterport.com/show/?m=i65DfCK4ymG",
            "https://my.matterport.com/show/?m=zyGpVU6U4f6",
            "https://my.matterport.com/show/?m=HG95saF1HYb",
        ],
        "imagenes_rental_units": [
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W006-900x720.jpg",
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W005-900x720.jpg",
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W007-900x720.jpg",
            "https://flipcoliving.com/wp-content/uploads/2023/10/Flipco-Cantueso-W008-900x720.jpg",
        ],
        "city_name": "Madrid",
        "referenceCode": "Madrid-Cantueso-0001",
    }
]
