import logging
import random
import time
from math import ceil
from typing import Any

import curl_cffi

from model.listing_model import Listing
from misc.save_data import SaveData
from misc.url_parser import URLParser

logger = logging.getLogger(__name__)


class ZapRequest:
    def __init__(self, config: Any, filters: Any, **kwargs):
        self.base_url = config['base_url']
        self.parsed_api_url = URLParser(config['data_api'])
        self.session = curl_cffi.Session()
        self.user_id = None
        self.save_data = SaveData()
        self.save_data_json = True if config['save_json_listings'] == 'True' else False
        self.save_data_csv = True if config['save_json_listings'] == 'True' else False
        self.filters = filters
        self.get_user_id_from_cookies()

    def get_all(self) -> list[Listing]:
        zap_listings = []
        results_per_page = 100
        total_results = 1
        page_number = 1

        while page_number <= ceil(total_results / results_per_page):
            logger.info(f'Getting {results_per_page} results at page {page_number}')
            response = self.get(self.get_paginated_url(results_per_page, page_number))
            listing_json = response['search']['result']['listings']
            logger.info(f'Found {len(listing_json)} listings at page {page_number}')
            for listing in listing_json:
                listing_serialized = Listing(**listing)
                zap_listings.append(listing_serialized)
            if self.save_data_json:
                self.save_data.add_listings_json(listing_json)
            total_results = response['page']['uriPagination']['totalListingCounter']
            logger.info(f'There are {total_results} properties in total (page {page_number}/{ceil(total_results / results_per_page)})')
            page_number += 1

            if page_number <= ceil(total_results / results_per_page):
                sleep_seconds = random.randint(5, 10)
                logger.info(f'To avoid API blocks, will wait for {sleep_seconds} seconds before getting the next page')
                time.sleep(sleep_seconds)

        if self.save_data_csv:
            self.save_data.add_listings_csv(zap_listings)
            self.save_data.save_csv_listings(self.base_url)
        if self.save_data_json:
            self.save_data.save_json_listings()

        n_listings_before_filter = len(zap_listings)
        zap_listings = self.apply_filters(zap_listings)
        n_listings_after_filter = len(zap_listings)
        logger.info(f'Listing count - Before filtering: {n_listings_before_filter}, After filtering: {n_listings_after_filter}')

        return zap_listings

    def get_paginated_url(self, results_per_page: int, page_number: int) -> str:
        page_formatting_params = {
            'size': results_per_page,
            'page': page_number,
            'from': (page_number - 1) * results_per_page
        }
        self.parsed_api_url.replace_query_params(page_formatting_params)
        return self.parsed_api_url.parsed.geturl()

    def get(self, url: str) -> dict:
        ## x-domain is the only required header for this call
        headers = {
            'x-domain': '.zapimoveis.com.br'
        }
        response = self.session.get(url, impersonate='firefox', headers=headers)
        if response.status_code != 200:
            logger.error(f'Request failed with status code: {response.status_code}')
            raise Exception(f'Request failed with status code: {response.status_code}')
        return response.json()

    def get_user_id_from_cookies(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Referer': 'https://www.zapimoveis.com.br/',
            'x-domain': '.zapimoveis.com.br',
            'X-DeviceId': '93f2af3c-7628-4222-a145-2ca174305347',
            'Origin': 'https://www.zapimoveis.com.br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Priority': 'u=0',
        }
        response = self.session.get(self.base_url, headers=headers, impersonate='firefox')
        if response.status_code != 200:
            logger.error(f'Request failed with status code: {response.status_code}')
            raise Exception(f'Request failed with status code: {response.status_code}')
        cookies = self.session.cookies.get_dict()
        if 'z_user_id' not in cookies:
            logger.error(f'Could not find z_user_id in cookies')
            raise Exception(f'Could not find z_user_id in cookies')
        self.parsed_api_url.replace_query_params({'user': cookies['z_user_id']})
        logger.info(f'Got z_user_id from cookies: {cookies['z_user_id']}')

    def apply_filters(self, listings: list[Listing]) -> list[Listing]:
        rent_price_min = self.filters['rent_price_min'].strip()
        rent_price_min = float(rent_price_min) if rent_price_min.isdigit() else 0
        rent_price_max = self.filters['rent_price_max'].strip()
        rent_price_max = float(rent_price_max) if rent_price_max.isdigit() else 9999999
        neighborhood = self.filters['neighborhood'].strip()

        logger.info(f'Applying rent price filter - Min: {rent_price_min}, Max: {rent_price_max}')
        logger.info(f'Applying neighborhood filter for "{neighborhood}"')

        return list(filter(
            lambda listing: self.is_rent_price_ok(listing, rent_price_min, rent_price_max)
                            and self.is_neighborhood_ok(listing, neighborhood)
            , listings
        ))

    @staticmethod
    def is_rent_price_ok(listing: Listing, rent_price_min: float = 0, rent_price_max: int = 9999999) -> bool:
        rent_price = listing.listing.get_rental_pricing_info().price
        return rent_price_min <= rent_price <= rent_price_max

    @staticmethod
    def is_neighborhood_ok(listing: Listing, neighborhood: str) -> bool:
        if not neighborhood:
            return True
        return listing.listing.address.neighborhood == neighborhood