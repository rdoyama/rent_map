import json
import logging
import os.path
from datetime import datetime

from model.listing_model import Listing

logger = logging.getLogger(__name__)


class SaveData:
    def __init__(self):
        now = datetime.now()
        formatted_now = now.strftime("%Y%m%d-%H%M%S")
        self.subfolder_name = f'{formatted_now}'
        self.listings_json = []
        self.listings_csv = []

    def add_listings_json(self, listings: list[dict]):
        self.listings_json += listings

    def add_listings_csv(self, listings: list[Listing]):
        self.listings_csv += listings

    def create_directory_structure(self):
        if not os.path.isdir('data'):
            os.mkdir('data')
            logging.info('"data" folder created')
        if not os.path.isdir(f'data/{self.subfolder_name}'):
            os.mkdir(f'data/{self.subfolder_name}')
            logging.info(f'"data/{self.subfolder_name}" folder created')

    def save_json_listings(self):
        self.create_directory_structure()
        with open(f'data/{self.subfolder_name}/listings.json', 'w', encoding='utf-8') as json_file:
            json_file.write(json.dumps(self.listings_json, indent=4))
            logging.info('The JSON file "listings.json" has been saved successfully')

    def save_csv_listings(self, base_url: str):
        self.create_directory_structure()
        with open(f'data/{self.subfolder_name}/listings.csv', 'w', encoding='utf-8') as csv_file:
            for i, listing in enumerate(self.listings_csv):
                if i == 0:
                    csv_file.write(listing.get_csv_headers() + '\n')
                line = listing.get_csv_line(base_url)
                if line is not None:
                    csv_file.write(line + '\n')
