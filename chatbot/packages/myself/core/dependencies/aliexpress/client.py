from httpx import Client as HTTPXClient


class Client:
    def __init__(self, region: str, currency: str, locale: str, site: str) -> None:
        self.client = HTTPXClient(headers={
            "Host": "fr.aliexpress.com",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0"
        })
        self.client.cookies = {
            "aep_usuc_f": f"region={region}&site={site}&b_locale={locale}&c_tp={currency}",
        }
    
    def get(self, url: str, params: dict = {}) -> None:
        return self.client.get(url, params=params)

    def post(self, url: str, data: dict = {}) -> None:
        return self.client.post(url, data=data)