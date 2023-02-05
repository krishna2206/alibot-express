from fancify_text import bold

import config
from chatbot.utils import Payload
from chatbot.sharedinstances import msgr_api_components

from chatbot.packages.myself.core.config import LOCALE, REGION, SITE
from chatbot.packages.myself.core.customermodel import CustomerModel
from chatbot.packages.myself.core.dependencies.aliexpress import AliExpress

customer_model = CustomerModel(config)


def create_product_elements(current_page_list, **kwargs):
    customer_id = kwargs.get("customer_id")
    customer = customer_model.get_customer(customer_id)
    aliexpress = AliExpress(
        REGION, customer.get("currency"), LOCALE, SITE)
    elements = msgr_api_components.Elements()

    for p in current_page_list:
        product = aliexpress.get_product(p.get("id"))

        title = p.get("title")
        subtitle = f"{p['prices']['salePrice']['formattedPrice']}\n"
        if (p["trade"] is not None) or (p["rating"] is not None):
            subtitle += (
                "{}{}\n".format(
                    '' if p['trade'] is None else p['trade']['tradeDesc'],
                    '' if p['rating'] is None else f"- {p['rating']}/5"
                )
            )

        selling_points = p["sellingPoints"]
        if selling_points is not None:
            for idx in range(len(selling_points)):
                selling_points[idx]["tagContent"]["tagStyle"]["position"] = int(
                    selling_points[idx]["tagContent"]["tagStyle"]["position"])
            selling_points = sorted(selling_points, key=lambda sp: sp["tagContent"]["tagStyle"]["position"])

            for selling_point in selling_points:
                try:
                    subtitle += f"{selling_point['tagContent']['tagText']}\n"
                except KeyError:
                    continue

        subtitle += f"{p['store']['storeName']}"
        buttons = []

        # ? Show product on browser
        show_product_link = msgr_api_components.Button(
            button_type="web_url",
            title="🌐 Voir le produit")
        show_product_link.set_url(f"https://fr.aliexpress.com/item/{p['id']}.html")
        buttons.append(show_product_link.get_content())

        has_variants = len(product.get("prices")) > 1
        if has_variants:
            # ? List product variants
            list_variants_button = msgr_api_components.Button(
                button_type="postback",
                title="🌈 Voir les variantes")
            list_variants_button.set_payload(
                Payload(target_action="list_product_variants", product_id=p["id"]).get_content())
            buttons.append(list_variants_button.get_content())

        else:
            # ? Add product to cart
            add_to_cart_button = msgr_api_components.Button(
                button_type="postback",
                title="🛒 Ajouter au panier")
            add_to_cart_button.set_payload(
                Payload(
                    target_action="add_to_cart",
                    product_id=p["id"],
                    variant_id=None).get_content())
            buttons.append(add_to_cart_button.get_content())

        element = msgr_api_components.Element(
            title=title,
            subtitle=subtitle,
            image_url=p["image"],
            buttons=buttons
        )
        elements.add_element(element.get_content())

    return elements


def create_product_variant_elements(current_page_list, **kwargs):
    customer_id = kwargs.get("customer_id")
    product_id = kwargs.get("product_id")

    customer = customer_model.get_customer(customer_id)
    display_currency = "€" if customer.get("currency") == "EUR" else "$"
    elements = msgr_api_components.Elements()

    for variant in current_page_list:
        title = variant.get("variantName")
        subtitle = (
            "{} {} {}\n".format(
                f"{display_currency} {variant.get('promotionalPrice')}",
                _to_strikethrough(f"{display_currency} {variant.get('initialPrice')}"),
                bold(str(variant.get('discount')))) +
            f"Dispo : {variant.get('availQuantity')}"
        )

        # ? Show product on browser
        show_product_link = msgr_api_components.Button(
            button_type="web_url",
            title="🌐 Voir le produit")
        show_product_link.set_url(f"https://fr.aliexpress.com/item/{product_id}.html")

        # ? Add product to cart
        add_to_cart_button = msgr_api_components.Button(
            button_type="postback",
            title="🛒 Ajouter au panier")
        add_to_cart_button.set_payload(
            Payload(
                target_action="add_to_cart",
                product_id=product_id,
                variant_id=str(variant.get("variantId"))).get_content())

        element = msgr_api_components.Element(
            title=title,
            subtitle=subtitle,
            image_url=variant.get("variantImage"),
            buttons=[show_product_link.get_content(), add_to_cart_button.get_content()]
        )

        elements.add_element(element.get_content())

    return elements


def create_cart_product_elements(current_page_list, **kwargs):
    customer_id = kwargs.get("customer_id")

    customer = customer_model.get_customer(customer_id)
    display_currency = "€" if customer.get("currency") == "EUR" else "$"
    aliexpress = AliExpress(
        REGION, customer.get("currency"), LOCALE, SITE)
    elements = msgr_api_components.Elements()

    for cart_product in current_page_list:
        product = aliexpress.get_product(cart_product.get("product_id"))

        title = product.get("title")
        variant_id = cart_product.get("variant_id")
        if variant_id is not None:
            variant = _get_product_variant(variant_id, product.get("prices"))
        else:
            variant = product.get("prices")[0]

        subtitle = (
            "{} {} {}\n".format(
                f"{display_currency} {variant.get('promotionalPrice')}",
                _to_strikethrough(f"{display_currency} {variant.get('initialPrice')}"),
                bold(str(variant.get('discount')))) +
            f"Dispo : {variant.get('availQuantity')}"
        )

        # ? Show product on browser
        show_product_link = msgr_api_components.Button(
            button_type="web_url",
            title="🌐 Voir le produit")
        show_product_link.set_url(f"https://fr.aliexpress.com/item/{cart_product.get('product_id')}.html")

        # ? Remove to cart button
        remove_to_cart_button = msgr_api_components.Button(
            button_type="postback",
            title="❌ Retirer du panier")
        remove_to_cart_button.set_payload(
            Payload(
                target_action="remove_to_cart",
                product_id=cart_product.get("product_id")).get_content())
        
        element = msgr_api_components.Element(
            title=title,
            subtitle=subtitle,
            image_url=(
                product.get("images")[0] if variant.get("variantImage") is None
                else variant.get("variantImage")),
            buttons=[show_product_link.get_content(), remove_to_cart_button.get_content()]
        )

        elements.add_element(element.get_content())

    return elements


#? Check if a product is already in the cart
def _check_cart_product(product_id: str, cart: list) -> bool:
    if len(cart) == 0:
        return False

    for product in cart:
        if product["product_id"] == product_id:
            return True
    return False


def _get_product_variant(variant_id: int, variants: list):
    for variant in variants:
        if variant.get("variantId") == variant_id:
            return variant
    return None


def _to_strikethrough(text):
    return "".join(u"\u0336" + char for char in text) + u"\u0336"
