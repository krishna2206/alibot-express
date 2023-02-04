from .client import Client
from .product import get_product
from .search import search_product


class AliExpress:
    def __init__(self, region: str, currency: str, locale: str, site: str) -> None:
        self.client = Client(
            region=region,
            currency=currency,
            locale=locale,
            site=site
        )

    def search_product(self, query: str, page: int = 1) -> None:
        return search_product(self.client, query, page)

    def get_product(self, product_id: str) -> None:
        return get_product(self.client, product_id)