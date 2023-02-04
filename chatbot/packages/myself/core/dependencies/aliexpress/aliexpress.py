import re
import json

from httpx import Client
from bs4 import BeautifulSoup


class Utils:
    @staticmethod
    def clean_query(query: str) -> str:
        # Replace spaces with dashes, and remove all special characters
        return re.sub(r"[^a-zA-Z0-9-]", "", query.replace(" ", "-"))

    @staticmethod
    def get_value(keys: list, data: dict) -> str | int | dict | None:
        value = data
        for key in keys:
            try:
                value = value[key]
            except KeyError:
                return None
        return value


class AliExpress:
    def __init__(self, region: str, currency: str, locale: str, site: str) -> None:
        self.url = "https://fr.aliexpress.com"
        self.client = Client(headers={
            "Host": "fr.aliexpress.com",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0"
        })
        self.client.cookies = {
            "aep_usuc_f": f"region={region}&site={site}&b_locale={locale}&c_tp={currency}",
        }
        
    
    def search_product(self, query: str, page: int = 1) -> None:
        url = self.url + "/w/wholesale-" + Utils.clean_query(query) + ".html"
        response = self.client.get(url, params={"page": page})

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            js_data = self.__get_js_data(soup)

            if js_data:
                cleaned_data = self.__parse_js_data(js_data)

                if cleaned_data:
                    return cleaned_data
                raise Exception("Failed to parse js data.")

            raise Exception("Failed to get js data.")

        raise Exception(f"Error while fetching the page. {response.status_code} {response.reason_phrase}")

    def __get_js_data(self, soup: BeautifulSoup) -> dict | None:
        js_data = None
        scripts = soup.find_all("script")
        for script in scripts:
            if "window._dida_config_._init_data_= " in script.text:
                for line in script.text.splitlines():
                    if "window._dida_config_._init_data_= " in line:
                        js_data = line.replace("window._dida_config_._init_data_= ", "")
                        js_data = js_data.replace("data: ", "\"data\": ")
                        js_data = json.loads(js_data)
                        break
                break
        return js_data
    
    def __parse_js_data(self, js_data: dict) -> dict:
        cleaned_data = {}
        js_data = js_data["data"]["data"]["root"]["fields"]

        page_info = js_data["pageInfo"]
        cleaned_data["page"] = page_info["page"]
        cleaned_data["pageSize"] = page_info["pageSize"]
        cleaned_data["totalResults"] = page_info["totalResults"]

        result_items = js_data["mods"]["itemList"]["content"]
        cleaned_data["results"] = []
        for result_item in result_items:
            # print(result_item)
            # print("\n\n")

            result = {}
            result["id"] = Utils.get_value(["productId"], result_item)
            result["image"] = "https:" + Utils.get_value(["image", "imgUrl"], result_item)
            result["title"] = Utils.get_value(["title", "displayTitle"], result_item)
            result["prices"] = Utils.get_value(["prices"], result_item)
            result["sellingPoints"] = Utils.get_value(["sellingPoints"], result_item)
            result["store"] = Utils.get_value(["store"], result_item)
            result["rating"] = Utils.get_value(["evaluation", "starRating"], result_item)
            result["trade"] = Utils.get_value(["trade"], result_item)

            """
            result["link"] = result_item["link"]
            result["reviews"] = result_item["reviews"]
            result["orders"] = result_item["orders"]
            result["shipping"] = result_item["shipping"]
            """

            cleaned_data["results"].append(result)
        return cleaned_data

    def get_product(self, product_id: str):
        url = self.url + "/item/" + product_id + ".html"
        response = self.client.get(url)
        print(response.text)


if __name__ == "__main__":
    aliexpress = AliExpress(
        region="MG",
        currency="EUR",
        locale="fr_FR",
        site="fra"
    )

    # products = aliexpress.search_product("hp pavilion gaming")
    # print(products)

    product = aliexpress.get_product("1005003425535578")
