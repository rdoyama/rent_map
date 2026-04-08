import configparser
import logging
import sys

from custom_requests.base_request import ZapRequests
from kmz.kmz import KMZ
from misc.filters import ListingFilterEngine
from misc.multiple_data_apis import get_all_apis
from misc.save_data import SaveData

logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('Logs.log'),
        ],
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    config = configparser.RawConfigParser()
    config.read('config.ini')

    filters = config['FILTERS']
    filter_engine = ListingFilterEngine.from_config(filters)

    utilities = config['UTILITY']
    kmz = KMZ(utilities)

    zap_configs = config['ZAP']
    apis = get_all_apis(zap_configs)
    zap_api = ZapRequests(zap_configs)
    zap_listings = []

    for api in apis:
        zap_api.set_parsed_api_url(api)
        zap_listings += zap_api.get_all()

    zap_listings = filter_engine.apply(zap_listings)

    if len(zap_listings) == 0:
        return

    if zap_configs['save_csv'] == 'True':
        SaveData(zap_configs, zap_listings).save()

    kmz.set_base_url(zap_configs['base_url'])
    kmz.process_listings(zap_listings)

    kmz.add_utilities()
    kmz.generate_kmz()


if __name__ == '__main__':
    main()