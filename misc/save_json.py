import json
import logging
import os.path
from datetime import datetime

from custom_requests.zap_listing_model import ZapListing

logger = logging.getLogger(__name__)


class SaveJSON:
    def __init__(self):
        now = datetime.now()
        formatted_now = now.strftime("%Y%m%d-%H%M%S")
        self.subfolder_name = f'{formatted_now}_json'
        self.listings = []

    def add_listings(self, listings: list[ZapListing]):
        self.listings += listings

    def save_json_listings(self):
        if not os.path.isdir('data'):
            os.mkdir('data')
            logging.info('"data" folder created')
        if not os.path.isdir(f'data/{self.subfolder_name}'):
            os.mkdir(f'data/{self.subfolder_name}')
            logging.info(f'"data/{self.subfolder_name}" folder created')
        with open(f'data/{self.subfolder_name}/listings.json', 'w', encoding='utf-8') as json_file:
            json_file.write(json.dumps(self.listings, indent=4))
            logging.info('The JSON file "listings.json" has been saved successfully')