import json

from bs4 import BeautifulSoup

from .utils import Utils
from .constants import URL


def search_product(client, query: str, page: int = 1) -> None:
    url = URL + "/w/wholesale-" + Utils.clean_query(query) + ".html"
    response = client.get(url, params={"page": page})

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        js_data = __get_js_data(soup)

        if js_data:
            cleaned_data = __parse_js_data(js_data)

            if cleaned_data:
                return cleaned_data
            raise Exception("Failed to parse js data.")

        raise Exception("Failed to get js data.")

    raise Exception(f"Error while fetching the page. {response.status_code} {response.reason_phrase}")


def __get_js_data(soup: BeautifulSoup) -> dict | None:
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


def __parse_js_data(js_data: dict) -> dict:
    cleaned_data = {}
    js_data = js_data["data"]["data"]["root"]["fields"]

    page_info = js_data["pageInfo"]
    cleaned_data["page"] = page_info["page"]
    cleaned_data["pageSize"] = page_info["pageSize"]
    cleaned_data["totalResults"] = page_info["totalResults"]

    result_items = js_data["mods"]["itemList"]["content"]
    cleaned_data["results"] = []
    i = 3
    for result_item in result_items:

        """
        if i == 3:
            print(result_item)
            i += 1
        """

        result = {}
        result["id"] = Utils.get_value(["productId"], result_item)
        result["image"] = "https:" + Utils.get_value(["image", "imgUrl"], result_item)
        result["title"] = Utils.get_value(["title", "displayTitle"], result_item)

        result["prices"] = Utils.get_value(["prices"], result_item)
        result["sellingPoints"] = Utils.get_value(["sellingPoints"], result_item)
        result["store"] = Utils.get_value(["store"], result_item)
        result["rating"] = Utils.get_value(["evaluation", "starRating"], result_item)
        result["trade"] = Utils.get_value(["trade"], result_item)

        cleaned_data["results"].append(result)
    return cleaned_data
