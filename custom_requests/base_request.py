import logging
import random
import time
from math import ceil
from typing import Any

import curl_cffi

from misc.listing_filter import ListingFilter
from model.listing_model import Listing
from misc.save_data import SaveData
from misc.url_parser import URLParser

logger = logging.getLogger(__name__)


class BaseRequest(ListingFilter):
    def __init__(self, config: Any, filters: Any, website_name: str, **kwargs):
        super().__init__(filters)
        self.base_url = config['base_url']
        self.parsed_api_url = URLParser(config['data_api'])
        self.session = curl_cffi.Session()
        self.user_id = None
        self.website_name = website_name
        self.save_data = SaveData(self.website_name)
        self.save_data_json = True if config['save_json_listings'] == 'True' else False
        self.save_data_csv = True if config['save_csv_listings'] == 'True' else False
        self.get_user_id_from_cookies()

    def get_all(self) -> list[Listing]:
        zap_listings = []
        results_per_page = 110
        total_results = 1
        page_number = 1

        while page_number <= ceil(total_results / results_per_page):
            logger.info(f'({self.website_name}) Getting {results_per_page} results at page {page_number}')
            response = self.get(self.get_paginated_url(results_per_page, page_number))
            listing_json = response['search']['result']['listings']
            logger.info(f'({self.website_name}) Found {len(listing_json)} listings at page {page_number}')
            for listing in listing_json:
                listing_serialized = Listing(**listing)
                zap_listings.append(listing_serialized)
            if self.save_data_json:
                self.save_data.add_listings_json(listing_json)

            uri_pagination = response['page']['uriPagination']
            if 'totalListingCounter' in uri_pagination:
                total_results = uri_pagination['totalListingCounter']
            else:
                total_results = uri_pagination['total']
            logger.info(f'({self.website_name}) There are {total_results} properties in total (page {page_number}/{ceil(total_results / results_per_page)})')
            page_number += 1

            if page_number <= ceil(total_results / results_per_page):
                sleep_seconds = random.randint(2, 4)
                logger.info(f'({self.website_name}) To avoid API blocks, will wait for {sleep_seconds} seconds before getting the next page')
                time.sleep(sleep_seconds)

        if self.save_data_csv:
            self.save_data.add_listings_csv(zap_listings)
            self.save_data.save_csv_listings(self.base_url)
        if self.save_data_json:
            self.save_data.save_json_listings()

        n_listings_before_filter = len(zap_listings)
        zap_listings = self.apply_filters(zap_listings)
        n_listings_after_filter = len(zap_listings)
        logger.info(f'({self.website_name}) Listing count - Before filtering: {n_listings_before_filter}, After filtering: {n_listings_after_filter}')

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
            'x-domain': f'.{self.website_name}.com.br'
        }
        response = self.session.get(url, impersonate='firefox', headers=headers)
        if response.status_code != 200:
            logger.error(f'({self.website_name}) Request failed with status code: {response.status_code}')
            raise Exception(f'({self.website_name}) Request failed with status code: {response.status_code}')
        return response.json()

    def get_user_id_from_cookies(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Referer': f'https://www.{self.website_name}.com.br/',
            'x-domain': f'.{self.website_name}.com.br',
            'X-DeviceId': '93f2af3c-7628-4222-a145-2ca174305347',
            'Origin': f'https://www.{self.website_name}.com.br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Priority': 'u=0',
        }
        response = self.session.get(self.base_url, headers=headers, impersonate='firefox')
        if response.status_code != 200:
            logger.error(f'({self.website_name}) Request failed with status code: {response.status_code}')
            raise Exception(f'({self.website_name}) Request failed with status code: {response.status_code}')
        cookies = self.session.cookies.get_dict()
        if 'z_user_id' not in cookies:
            logger.error(f'({self.website_name}) Could not find z_user_id in cookies')
            raise Exception(f'({self.website_name}) Could not find z_user_id in cookies')
        self.parsed_api_url.replace_query_params({'user': cookies['z_user_id']})
        logger.info(f'({self.website_name}) Got z_user_id from cookies: {cookies['z_user_id']}')