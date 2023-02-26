import json

from bs4 import BeautifulSoup

from .utils import Utils
from .constants import URL


def get_product(client, product_id: str):
    url = URL + "/item/" + product_id + ".html"
    response = client.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        js_data = __get_js_data(soup)

        if js_data:
            cleaned_data = __parse_js_data(js_data)

            if cleaned_data:
                return cleaned_data
            raise Exception("Failed to parse js data.")

        raise Exception("Failed to get js data.")

    raise Exception(
        f"Error while fetching the page. {response.status_code} {response.reason_phrase}")


def __get_js_data(soup: BeautifulSoup):
    js_data = None
    scripts = soup.find_all("script")
    for script in scripts:
        if "window.runParams = " in script.text:
            js_data = script.text
            lines = js_data.splitlines()
            for line in lines:
                if "data: " in line:
                    js_data = line.replace(
                        "data: ", "{ \"data\": ").rstrip(",") + "}"
                    js_data = json.loads(js_data)
                    break
            break
    return js_data


def __parse_js_data(js_data: dict):
    cleaned_data = {}

    js_data = js_data["data"]

    cleaned_data["id"] = Utils.get_value(["pageModule", "productId"], js_data)
    cleaned_data["title"] = Utils.get_value(["titleModule", "subject"], js_data)
    cleaned_data["description"] = Utils.get_value(
        ["pageModule", "description"], js_data)
    cleaned_data["images"] = Utils.get_value(
        ["imageModule", "imagePathList"], js_data)

    cleaned_data["prices"] = []
    try:
        has_variants = len(Utils.get_value(
            ["skuModule", "skuPriceList"], js_data)) > 1
    except TypeError:
        has_variants = False

    variant_data = (
        Utils.get_value(
            ["skuModule", "productSKUPropertyList", 0, "skuPropertyValues"],
            js_data)
        if has_variants
        else [{'skuPropertyImagePath': None}] * len(Utils.get_value(["skuModule", "skuPriceList"], js_data))
    )

    for variant_visual, variant_price in zip(
        variant_data,
        Utils.get_value(["skuModule", "skuPriceList"], js_data)
    ):
        cleaned_data["prices"].append({
            "variantId": Utils.get_value(["skuId"], variant_price),
            "variantName": Utils.get_value(["propertyValueDisplayName"], variant_visual),
            "variantImage": Utils.get_value(["skuPropertyImagePath"], variant_visual),
            "salable": Utils.get_value(["salable"], variant_price),
            "availQuantity": Utils.get_value(["skuVal", "availQuantity"], variant_price),
            "discount": (
                Utils.get_value(["skuVal", "discount"], variant_price)
                if Utils.get_value(["skuVal", "discount"], variant_price) is None
                else int(Utils.get_value(["skuVal", "discount"], variant_price))),
            "promotionalPrice": Utils.get_value(["skuVal", "skuActivityAmount", "value"], variant_price),
            "initialPrice": Utils.get_value(["skuVal", "skuAmount", "value"], variant_price),
        })

    cleaned_data["deliveryDetails"] = {}
    deliveryDetailsData = Utils.get_value(
        ["shippingModule", "generalFreightInfo",
            "originalLayoutResultList", 0, "bizData"],
        js_data)
    cleaned_data["deliveryDetails"]["providerName"] = Utils.get_value(
        ["deliveryProviderName"], deliveryDetailsData)
    cleaned_data["deliveryDetails"]["deliveryDayMin"] = Utils.get_value(
        ["deliveryDayMin"], deliveryDetailsData)
    cleaned_data["deliveryDetails"]["deliveryDayMax"] = Utils.get_value(
        ["deliveryDayMax"], deliveryDetailsData)
    cleaned_data["deliveryDetails"]["guaranteedDeliveryTime"] = Utils.get_value(
        ["guaranteedDeliveryTime"], deliveryDetailsData)
    cleaned_data["deliveryDetails"]["guaranteedDeliveryTime"] = Utils.get_value(
        ["guaranteedDeliveryTime"], deliveryDetailsData)
    cleaned_data["deliveryDetails"]["shipFrom"] = {}
    cleaned_data["deliveryDetails"]["shipFrom"]["code"] = Utils.get_value(
        ["shipFromCode"], deliveryDetailsData)
    cleaned_data["deliveryDetails"]["shipFrom"]["name"] = Utils.get_value(
        ["shipFrom"], deliveryDetailsData)
    cleaned_data["deliveryDetails"]["shipTo"] = {}
    cleaned_data["deliveryDetails"]["shipTo"]["code"] = Utils.get_value(
        ["shipToCode"], deliveryDetailsData)
    cleaned_data["deliveryDetails"]["shipTo"]["name"] = Utils.get_value(
        ["shipTo"], deliveryDetailsData)
    cleaned_data["shippingFee"] = Utils.get_value(
        ["displayAmount"], deliveryDetailsData)

    return cleaned_data
