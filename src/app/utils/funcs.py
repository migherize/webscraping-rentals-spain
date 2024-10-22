import re
from datetime import datetime, timedelta
from app.models.enums import Month


def get_month_dates(text):
    regex = (
        r"(january|february|march|april|may|june|july|august|september|october|november|december|"
        r"enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)"
    )

    match = re.search(regex, text, re.IGNORECASE)

    if match:
        month_name = match.group(1).lower()
        current_year = datetime.now().year
        current_month = datetime.now().month

        try:
            month_enum = Month[month_name.upper()]
        except KeyError:
            return None, None

        month = month_enum.value

        year = current_year if month >= current_month else current_year + 1

        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year, month, 31)
        else:
            next_month = datetime(year, month + 1, 1)
            end_date = next_month - timedelta(days=1)

        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

    else:
        return None, None


def find_feature_keys(features_list: str, feature_map: dict):
    features_text = ', '.join(features_list)
    text = features_text.lower()
    matched_features = []
    # TODO:bug pets allowed
    for feature_key, terms in feature_map.items():
        for term in terms:
            if re.search(r"\b" + re.escape(term) + r"\b", text):
                matched_features.append(feature_key)
                break

    return matched_features
