import os
import csv
import pandas as pd
from app.models.schemas import Property, RentalUnits
from app.models.enums import custom_map, friendly_headers,feature_map
from app.config.settings import BASE_DIR
from typing import Optional

class CsvExporter:
    def __init__(self, output_path: str):
        self.custom_map = custom_map
        self.friendly_headers = friendly_headers
        self.feature_headers_map = feature_map
        self.output_path = os.path.join(BASE_DIR, "data", output_path, "CsvExporter.csv")

        if os.path.isfile(self.output_path):
            os.remove(self.output_path)

    def process_and_export_to_csv(self, property_object: Property, rental_unit_object: Optional[RentalUnits] = None):
        property_dict = property_object.model_dump()
        rental_unit_dict = rental_unit_object.model_dump() if rental_unit_object else {}

        property_dict = self.transform_features(property_dict, self.feature_headers_map)
        rental_unit_dict = self.transform_features(rental_unit_dict, self.feature_headers_map)

        property_dict = self.simplify_images_field(property_dict)
        rental_unit_dict = self.simplify_images_field(rental_unit_dict)

        headers = list(self.custom_map.keys())
        row = self.map_row(property_dict, rental_unit_dict, headers, self.custom_map)
        file_exists = os.path.isfile(self.output_path)
        with open(self.output_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            if not file_exists:
                writer.writerow(headers)
                writer.writerow(self.friendly_headers)
            writer.writerow(row)


    @staticmethod
    def get_labels_by_ids(ids, features):
        id_to_label = {feature["id"]: feature["label"] for feature in features}
        return [id_to_label.get(i) for i in ids if i in id_to_label]

    @staticmethod
    def extract_value(obj: dict, path: str):
        parts = path.split(".")
        for part in parts:
            if isinstance(obj, dict) and part in obj:
                obj = obj[part]
            else:
                return None
        return obj

    @staticmethod
    def transform_features(obj, fmap):
        ids = obj.get("Features", [])
        new_features = {}
        for fid in ids:
            key = str(fid)
            if key in fmap:
                label = fmap[key]
                new_features[label] = "Yes"
        obj["Features"] = new_features
        return obj

    @staticmethod
    def simplify_images_field(data: dict) -> dict:
        if "Images" in data:
            data["Images"] = [img["image"] for img in data["Images"] if "image" in img]
        return data

    @classmethod
    def map_row(cls, property_data: dict, rental_unit_data: dict, columns: list[str], custom_map: dict) -> list:
        row = []
        for column in columns:
            source = custom_map.get(column)
            if source is None:
                row.append(None)
            else:
                if column.startswith("property."):
                    value = cls.extract_value(property_data, source)
                elif column.startswith("ru."):
                    value = cls.extract_value(rental_unit_data, source)
                else:
                    value = None
                row.append(value)
        return row

    @staticmethod
    def save_to_csv(filename: str, columns: list[str], list_rows: list[list]):
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(columns)
            writer.writerows(list_rows)

    @staticmethod
    def read_excel_multiheaders(filepath: str, header_rows: int = 2) -> list[tuple]:
        df = pd.read_excel(filepath, header=list(range(header_rows)))
        return list(df.columns)

    @staticmethod
    def get_second_level_headers(headers: list[tuple]) -> list[str]:
        return [h[1] for h in headers if isinstance(h, tuple) and len(h) > 1]
