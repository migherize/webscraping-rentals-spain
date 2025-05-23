from app.models.enums import Pages
import app.scrapy.funcs as funcs
from pprint import pprint
from logging import Logger
from app.models.schemas import mapping
from app.scrapy.common import (
    parse_elements, 
    create_json, 
    read_json
)
from app.scrapy.yugo.yugo.yugo.utils import (
    retrive_lodgerin_property,
    retrive_lodgerin_rental_units,
)
from app.models.enums import Pages
from app.services.csvexport import CsvExporter

def etl_data_yugo(output_path: str, logger: Logger, context) -> None:

    items: list[dict[str, str]] = read_json(output_path)
    if items == []:
        logger.warning('- La data se encuentra vacia')
        return None

    elements_dict = parse_elements(context, mapping)
    list_api_key = elements_dict["api_key"].data
    exporter = CsvExporter(Pages.yugo.value)

    for index_property, data in enumerate(items):
        data = data["items_output"]

        # ---------------------------------------------------------------------------------------
        # Property
        data["yugo_space_name"] = data["yugo_space_name"].replace('Yugo', '').strip()
        data_property, api_key = retrive_lodgerin_property(
            data, elements_dict, list_api_key
        )
        if not api_key:
            logger.warning("No se obtuvo la API_key para la propiedad numero: %s", [index_property, api_key, data_property])
            continue

        property_id = funcs.save_property(data_property, api_key)
        logger.info("property_id: %s", property_id)
        data_property.id = property_id
        create_json(data_property, Pages.yugo.value)

        # ---------------------------------------------------------------------------------------
        # RentalUnit
        if not data["all_rental_units"]:
            logger.warning('No presenta rental units la propiedad numero: %s', index_property)
            continue

        data_rental_units, calendar_unit_list = (
            retrive_lodgerin_rental_units(
                data_property, elements_dict, data["all_rental_units"]
            )
        )
        list_rental_unit_id = []
        for rental_unit in data_rental_units:
            create_json(rental_unit, Pages.yugo.value)
            rental_unit_id = funcs.save_rental_unit(rental_unit, api_key)
            rental_unit.id = rental_unit_id
            list_rental_unit_id.append(rental_unit)
            exporter.process_and_export_to_csv(data_property, rental_unit)

        # ---------------------------------------------------------------------------------------
        # schedule
        for rental_id, calendar_unit in zip(
            list_rental_unit_id, calendar_unit_list
        ):
            if calendar_unit.startDate == "None":
                continue
            funcs.check_and_insert_rental_unit_calendar(
                rental_id.id, calendar_unit, api_key
            )

        for calendar_unit in calendar_unit_list:
            create_json(calendar_unit, Pages.yugo.value)