import configparser
import logging
import sys

from custom_requests.base_request import BaseRequest
from kmz.kmz import KMZ

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

    filters_kmz = config['FILTERS_KMZ']

    zap_configs = config['ZAP']
    zap_api = BaseRequest(zap_configs, filters_kmz, 'zapimoveis')
    zap_listings = zap_api.get_all()

    utilities = config['UTILITY']
    kmz = KMZ(utilities)

    kmz.set_base_url(zap_configs['base_url'])
    kmz.process_listings(zap_listings)

    kmz.add_utilities()
    kmz.generate_kmz()


if __name__ == '__main__':
    main()