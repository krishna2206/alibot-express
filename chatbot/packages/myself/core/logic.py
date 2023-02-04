from chatbot.utils import Payload
from chatbot.sharedinstances import msgr_api_components


def create_product_elements(current_page_list):
    elements = msgr_api_components.Elements()

    for product in current_page_list:
        title = product.get("title")
        subtitle = f"{product['prices']['salePrice']['formattedPrice']}\n"
        if (product["trade"] is not None) or (product["rating"] is not None):
            subtitle += (
                "{}{}\n".format(
                    '' if product['trade'] is None else product['trade']['tradeDesc'],
                    '' if product['rating'] is None else f"- {product['rating']}/5"
                )
            )

        selling_points = product["sellingPoints"]
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

        subtitle += f"{product['store']['storeName']}"

        show_product_link = msgr_api_components.Button(
            button_type="web_url",
            title="🌐 Voir le produit")
        show_product_link.set_url(f"https://fr.aliexpress.com/item/{product['id']}.html")

        add_to_cart_button = msgr_api_components.Button(
            button_type="postback",
            title="🛒 Ajouter au panier")
        add_to_cart_button.set_payload(
            Payload(target_action="add_to_cart", product_id=product["id"]).get_content())

        element = msgr_api_components.Element(
            title=title,
            subtitle=subtitle,
            image_url=product["image"],
            buttons=[
                show_product_link.get_content(),
                add_to_cart_button.get_content()
            ]
        )
        elements.add_element(element.get_content())

    return elements
