import logging
from typing import Any
from urllib.parse import urlparse, parse_qs, parse_qsl, ParseResult, urlencode

logger = logging.getLogger(__name__)

class URLParser:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.parsed = urlparse(base_url)

    def get_param(self, name: str) -> Any:
        query_params = self.parsed.query
        print(query_params)

    def replace_param(self, param_name: str, new_value: Any):
        params = parse_qs(self.parsed.query)
        params[param_name] = new_value  # change query param here
        self.parsed = ParseResult(scheme=self.parsed.scheme, netloc=self.parsed.hostname, path=self.parsed.path, params=self.parsed.params, query=urlencode(params),
                          fragment=self.parsed.fragment)

    def replace_query_params(self, params: dict, add_if_not_exist: bool = False):
        query = dict(parse_qsl(self.parsed.query))
        if not add_if_not_exist:
            params = {key: value for key, value in params.items() if key in query}
        query.update(params)
        self.parsed = self.parsed._replace(query=urlencode(query))