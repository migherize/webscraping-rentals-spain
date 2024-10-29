import re
from datetime import datetime, timedelta
from app.models.enums import Month, PropertyType, ContractModels
from app.utils.lodgerinService import LodgerinAPI
import app.utils.constants as constants

def get_month_dates(text):
    regex = r'(january|february|march|april|may|june|july|august|september|october|november|december|' \
            r'enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)'

    match = re.search(regex, text, re.IGNORECASE)
    
    if match:
        month_name = match.group(1).lower() 
        current_date = datetime.now()
        start_date = current_date.strftime('%Y-%m-%d')
        
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
        
        return start_date, end_date.strftime('%Y-%m-%d')
    else:
        return None, None

def find_feature_keys(features_list: str, feature_map: dict):
    features_text = ", ".join(features_list)
    text = features_text.lower()
    matched_features = []
    for feature_key, terms in feature_map.items():
        for term in terms:
            if re.search(r"(?<!\bnot\b\s)(?<!\bno\b\s)\b" + re.escape(term) + r"\b", text):
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
        print("Tipo de búsqueda no válido:", term)
        return None

    if elements:
        contract_types = elements.get("data", [])
        
        for contract_type in contract_types:
            if contract_type.get("name") == term:
                return contract_type.get("id")
        return None
    else:
        print("Error en la solicitud:", elements)
        return None
