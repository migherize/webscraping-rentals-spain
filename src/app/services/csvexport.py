import os
import csv
import pandas as pd
from app.models.schemas import Property, RentalUnits
from app.models.enums import custom_map, friendly_headers,feature_map

class CsvExporter:
    def __init__(self):
        self.custom_map = custom_map
        self.friendly_headers = friendly_headers
        self.feature_headers_map = feature_map
    
    def process_and_export_to_csv(self, property_data, rental_unit_data, output_path):
        property_object = Property(**property_data)
        rental_unit_object = RentalUnits(**rental_unit_data)

        property_dict = property_object.model_dump()
        rental_unit_dict = rental_unit_object.model_dump()

        property_dict = self.transform_features(property_dict, self.feature_headers_map)
        rental_unit_dict = self.transform_features(rental_unit_dict, self.feature_headers_map)

        property_dict = self.simplify_images_field(property_dict)
        rental_unit_dict = self.simplify_images_field(rental_unit_dict)

        headers = list(self.custom_map.keys())
        row = self.map_row(property_dict, rental_unit_dict, headers, self.custom_map)

        file_exists = os.path.isfile(output_path)

        with open(output_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
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

if __name__ == "__main__":
    property_data = {
    "CountersRU": None,
    "Features": [15, 20, 21, 39, 42],
    "Images": [
        {
            "id": None,
            "image": "https://www.vitastudent.com/wp-content/uploads/2022/12/DSC1187.jpg",
            "isCover": True,
        },
        {
            "id": None,
            "image": "https://www.vitastudent.com/wp-content/uploads/2022/12/DSC2423-HDR.jpg",
            "isCover": False,
        },
        {
            "id": None,
            "image": "https://www.vitastudent.com/wp-content/uploads/2022/12/DSC2640-HDR.jpg",
            "isCover": False,
        },
        {
            "id": None,
            "image": "https://www.vitastudent.com/wp-content/uploads/2022/12/DSC2503-HDR.jpg",
            "isCover": False,
        },
        {
            "id": None,
            "image": "https://www.vitastudent.com/wp-content/uploads/2022/12/DSC2452-HDR.jpg",
            "isCover": False,
        },
        {
            "id": None,
            "image": "https://www.vitastudent.com/wp-content/uploads/2022/12/DSC2548-HDR-2358x1574-166850d.jpg",
            "isCover": False,
        },
        {
            "id": None,
            "image": "https://www.vitastudent.com/wp-content/uploads/2022/12/DSC2558-HDR.jpg",
            "isCover": False,
        },
        {
            "id": None,
            "image": "https://www.vitastudent.com/wp-content/uploads/2022/12/DSC2587-HDR.jpg",
            "isCover": False,
        },
        {
            "id": None,
            "image": "https://www.vitastudent.com/wp-content/uploads/2022/12/DSC2515-HDR.jpg",
            "isCover": False,
        },
        {
            "id": None,
            "image": "https://www.vitastudent.com/wp-content/uploads/2022/12/DSC2600-HDR.jpg",
            "isCover": False,
        },
        {
            "id": None,
            "image": "https://www.vitastudent.com/wp-content/uploads/2022/12/DSC2612-HDR.jpg",
            "isCover": False,
        },
        {
            "id": None,
            "image": "https://www.vitastudent.com/wp-content/uploads/2022/12/VS_Floorplans_Barcelona_Poblenou_2023.pdf",
            "isCover": False,
        },
    ],
    "Location": {
        "address": "Carrer de Sancho de Ávila, 2, Sant Martí, 08018 Barcelona, Spain",
        "city": "Barcelona",
        "country": "Spain",
        "countryCode": "ES",
        "fullAddress": "Carrer de Sancho de Ávila, 2, Sant Martí, 08018 Barcelona, Spain",
        "number": "2",
        "postalCode": "08018",
        "prefixPhone": "+34",
        "state": "Catalunya",
        "street": "Carrer de Sancho de Ávila",
        "lat": "41.3964845",
        "lon": "2.1874202",
    },
    "PropertyType": None,
    "Texts": {
        "description_en": "Our second student building to open in Barcelona  in the cool and urban district of Poblenou. This student accommodation is ideal if you're attending Pompeu Fabra University and want to be a part of the most forward-thinking neighbourhoods in Europe.",
        "description_es": "\n                Nuestro segundo edificio abierto en Barcelona, en el fresco y urbano barrio de Poblenou. Ideal si estudias en la Universitat Pompeu Fabra y quieres formar parte de uno de los barrios más vanguardistas de Europa.            ",
        "title_en": "Poblenou",
        "title_es": "Poblenou",
    },
    "areaM2": None,
    "code": None,
    "createdAt": None,
    "id": "ee08d058-192b-46ba-b5fa-970e6017cdbd",
    "isActive": True,
    "isEntirePropertyRental": None,
    "isPublished": True,
    "maxOccupancy": None,
    "provider": None,
    "providerRef": None,
    "referenceCode": "Poblenou_barcelona",
    "rentalType": "individual",
    "typeSize": None,
    "updatedAt": None,
    "areaM2Available": None,
    "dateLastReform": None,
    "numBathrooms": "3",
    "videoUrl": None,
    "tourUrl": "https://my.matterport.com/show/?m=J4jAyDTGM8q",
    "PropertyTypeId": 1,
}

    rental_unit_data = {
        "PropertyId": "ee08d058-192b-46ba-b5fa-970e6017cdbd",
        "Images": [
            {
                "id": None,
                "image": "https://cdn.brandfolder.io/2EZAWJN8/at/f4c99pptvcmkc6fcv7xnmgn3/BCN_-_Poblenou_-_Room_1210_10_RT.auto?width=1024",
                "isCover": True,
            },
            {
                "id": None,
                "image": "https://cdn.brandfolder.io/2EZAWJN8/at/kb6qr86gp75h2q65skshk4ck/BCN_-_Poblenou_-_Room_1210_2_RT.auto?width=1024",
                "isCover": False,
            },
            {
                "id": None,
                "image": "https://cdn.brandfolder.io/2EZAWJN8/at/5j33f93w9rbt692nb37vpfwh/BCN_-_Poblenou_-_Room_1210_5_RT.auto?width=1024",
                "isCover": False,
            },
            {
                "id": None,
                "image": "https://cdn.brandfolder.io/2EZAWJN8/at/k4nht3bp5r9qgj98gxg4jcwv/BCN_-_Poblenou_-_Room_1210_6_RT.auto?width=1024",
                "isCover": False,
            },
            {
                "id": None,
                "image": "https://cdn.brandfolder.io/2EZAWJN8/at/gq7n454jbxsh32tcbrj2cx/BCN_-_Poblenou_-_Room_1210_7_RT.auto?width=1024",
                "isCover": False,
            },
            {
                "id": None,
                "image": "https://cdn.brandfolder.io/2EZAWJN8/at/smpkjwp9xm44hqpnn6b8ztb/BCN_-_Poblenou_-_Room_1210_8_RT.auto?width=1024",
                "isCover": False,
            },
            {
                "id": None,
                "image": "https://cdn.brandfolder.io/2EZAWJN8/at/ggc5fm5cg5n4kz27rhk3848/BCN_-_Poblenou_-_Room_1210_9_RT.auto?width=1024",
                "isCover": False,
            },
            {
                "id": None,
                "image": "https://cdn.brandfolder.io/2EZAWJN8/at/vpmch5hkvhkjbc3q69n59/BCN_-_Poblenou_-_Room_1211_1_RT.auto?width=1024",
                "isCover": False,
            },
            {
                "id": None,
                "image": "https://cdn.brandfolder.io/2EZAWJN8/at/nmpwp87srtp4483xnsx8pf3c/BCN_-_Poblenou_-_Room_1211_10_RT.auto?width=1024",
                "isCover": False,
            },
            {
                "id": None,
                "image": "https://cdn.brandfolder.io/2EZAWJN8/at/7trvsg53sq9cxh9wwfbjtc/BCN_-_Poblenou_-_Room_1211_2_RT.auto?width=1024",
                "isCover": False,
            },
            {
                "id": None,
                "image": "https://cdn.brandfolder.io/2EZAWJN8/at/sg85jbpsqw5nq8v4bv9mkck/BCN_-_Poblenou_-_Room_1211_3_RT.auto?width=1024",
                "isCover": False,
            },
            {
                "id": None,
                "image": "https://cdn.brandfolder.io/2EZAWJN8/at/s6kxwbtwv2fpx6rcgx3ccx/BCN_-_Poblenou_-_Room_1211_6_RT.auto?width=1024",
                "isCover": False,
            },
            {
                "id": None,
                "image": "https://cdn.brandfolder.io/2EZAWJN8/at/kk76sfnkqw6s47v44twt7xh5/BCN_-_Poblenou_-_Room_1211_7_RT.auto?width=1024",
                "isCover": False,
            },
        ],
        "Price": {
            "contractType": "monthly",
            "currency": "EUR",
            "amount": 1557,
            "depositAmount": 1557,
            "reservationAmount": 0,
            "discountPercent": None,
            "minPeriod": 1,
            "maxPeriod": None,
            "paymentCycle": "monthly",
        },
        "Texts": {
            "description_en": "Our second student building to open in Barcelona  in the cool and urban district of Poblenou. This student accommodation is ideal if you're attending Pompeu Fabra University and want to be a part of the most forward-thinking neighbourhoods in Europe.",
            "description_es": "\n                Nuestro segundo edificio abierto en Barcelona, en el fresco y urbano barrio de Poblenou. Ideal si estudias en la Universitat Pompeu Fabra y quieres formar parte de uno de los barrios más vanguardistas de Europa.            ",
            "title_en": "Poblenou",
            "title_es": "Poblenou",
        },
        "areaM2": 18,
        "areaM2Available": None,
        "bedType": None,
        "code": None,
        "createdAt": None,
        "dateLastReform": None,
        "id": "d76281c8-9564-4a3d-af1c-959a790035e2",
        "isActive": True,
        "isEnableCancellationPolicies": None,
        "isPublished": True,
        "level": None,
        "maxCapacity": None,
        "notes": None,
        "oldId": None,
        "propertyCode": None,
        "providerRef": None,
        "publicId": None,
        "referenceCode": "PN-337",
        "status": None,
        "typeSize": None,
        "updatedAt": None,
        "urlICalSync": None,
        "ExtraFeatures": None,
    }

    exporter = CsvExporter()
    exporter.process_and_export_to_csv(property_data, rental_unit_data, "output.csv")
