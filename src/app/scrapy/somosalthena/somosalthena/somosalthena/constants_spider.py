# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------

# Nombre base de la aranha base que se utilizara para el proyecto
BASE_NAME_MODEL = "somosalthena"

main_spider = f"{BASE_NAME_MODEL}_spider"

# ------------------------------------------------------------------------
# Datos directos si no se coloca informacion por consola
item_input_output_archive: dict[str, str] = {
    "output_folder_path": "./",
    "output_folder_name": r"data",
    "file_name": f"{BASE_NAME_MODEL}.json",
    "processed_name": f"{BASE_NAME_MODEL}" + "_refined.json",
    "refine": "0",
}

# ------------------------------------------------------------------------
# Encabezados para el archivo csv

item_main_spider: list[str] = [
    "items_output",
]

# ------------------------------------------------------------------------

# Diccionario que tendra los campos
# correspondientes segun el nombre de la aranha

spider_names: dict = {main_spider: item_main_spider}

# ------------------------------------------------------------------------

# cambios a realizar en el setting
item_custom_settings: dict[str, bool or str] = {
    "ROBOTSTXT_OBEY": False,
    "AUTOTHROTTLE_ENABLED": True,
    "LOG_LEVEL": "INFO",
}
