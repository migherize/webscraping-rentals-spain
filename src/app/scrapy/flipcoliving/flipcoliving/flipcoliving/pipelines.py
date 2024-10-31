# -*- coding: utf-8 -*-

import json
from os import path
from .constants import spider_names

class FlipcolivingPipeline:
    def open_spider(self, spider):
        # Create file path for JSON output
        self.json_path = path.join(spider.output_folder, spider.output_filename)
        # Initialize a list to hold items
        self.items = []

    def process_item(self, item, spider):
        # Add item to the list
        self.items.append(dict(item))  # Convert item to dict if it's not already
        return item

    def close_spider(self, spider):
        # Write the collected items to a JSON file
        with open(self.json_path, 'a', encoding='utf-8') as json_file:
            json.dump(self.items, json_file, ensure_ascii=False, indent=4)
