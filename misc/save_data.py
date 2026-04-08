import json
import logging
import os.path
from datetime import datetime

from model.listing_model import Listing

logger = logging.getLogger(__name__)


class SaveData:
    def __init__(self, config, listings: list[Listing], prefix: str = 'zapimoveis'):
        now = datetime.now()
        formatted_now = now.strftime("%Y%m%d-%H%M%S")
        self.subfolder_name = f'{formatted_now}'
        self.prefix = prefix
        self.base_url = config['base_url']
        self.listings = listings

    def create_directory_structure(self):
        if not os.path.isdir('data'):
            os.mkdir('data')
            logging.info('"data" folder created')
        if not os.path.isdir(f'data/{self.subfolder_name}'):
            os.mkdir(f'data/{self.subfolder_name}')
            logging.info(f'"data/{self.subfolder_name}" folder created')

    def save(self):
        self.create_directory_structure()
        with open(f'data/{self.subfolder_name}/{self.prefix}_listings.csv', 'w', encoding='utf-8') as csv_file:
            for i, listing in enumerate(self.listings):
                if i == 0:
                    csv_file.write(listing.get_csv_headers() + '\n')
                line = listing.get_csv_line(self.base_url)
                if line is not None:
                    csv_file.write(line + '\n')
