import configparser
import logging
import sys

from custom_requests.zap import ZapRequest
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

    zap_configs = config['ZAP']
    zap_api = ZapRequest(zap_configs)
    zap_listings = zap_api.get_all()

    kmz = KMZ(zap_listings, zap_configs)
    kmz.process_listings()


if __name__ == '__main__':
    main()