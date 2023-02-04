from split import chop

import config
from chatbot.utils import Payload
from chatbot.sharedinstances import send_api, msgr_api_components, user_model

from .core import logic
from .core.config import LOCALE, REGION, SITE
from .core.customermodel import CustomerModel
from .core.dependencies.aliexpress import AliExpress

customer_model = CustomerModel(config)
CURRENCY_MAP = {
    "EUR": "l'Euro",
    "USD": "le Dollar USD"
}


def ask_product_keyword(recipient_id):
    user_model.add_query(
        recipient_id,
        "send_search_result",
        page=1,
        subpage=1)

    send_api.send_text_message("💬 Quel produit voulez-vous rechercher ?", recipient_id)


def send_search_result(keywords, page, subpage, recipient_id):
    customer = customer_model.get_customer(recipient_id)
    aliexpress = AliExpress(
        REGION, customer.get("currency"), LOCALE, SITE)
    search_results = aliexpress.search_product(keywords, page)

    if len(search_results) == 0:
        send_api.send_text_message(
            "Il semblerait qu'il n'y ait aucun résultat à votre recherche 🤔",
            recipient_id)

        return False

    else:
        splitted_search_results = list(chop(10, search_results))
        if len(search_results) > 10:
            current_page_list = splitted_search_results[subpage - 1]
        else:
            current_page_list = search_results

        elements = logic.create_product_elements(current_page_list)
        quickreplies = msgr_api_components.QuickReplies()

        # ? Reiterate action button
        reiterate_button = msgr_api_components.QuickReply(
            title="Autre recherche",
            image_url="https://freeiconshop.com/wp-content/uploads/edd/refresh-flat.png",
            payload=Payload(
                target_action="ask_product_keyword").get_content())
        quickreplies.add_quick_reply(reiterate_button.get_content())

        #* Fin de la subpage
        if current_page_list == splitted_search_results[-1]:
            next_page = page + 1
            next_button = msgr_api_components.QuickReply(
                title="Suivant",
                image_url="https://icon-library.com/images/next-icon/next-icon-11.jpg",
                payload=Payload(
                    target_action="send_search_result",
                    keywords=keywords,
                    page=next_page,
                    subpage=1).get_content())
            quickreplies.add_quick_reply(next_button.get_content())

            print(send_api.send_generic_message(
                elements.get_content(),
                recipient_id,
                quick_replies=quickreplies.get_content(),
                image_aspect_ratio="square"))

        else:
            next_subpage = subpage + 1
            more_button = msgr_api_components.QuickReply(
                title="Voir plus",
                image_url="https://icon-library.com/images/next-icon/next-icon-11.jpg",
                payload=Payload(
                    target_action="send_search_result",
                    keywords=keywords,
                    page=page,
                    subpage=next_subpage).get_content())
            quickreplies.add_quick_reply(more_button.get_content())

            next_page = page + 1
            next_button = msgr_api_components.QuickReply(
                title="Suivant",
                image_url="https://icon-library.com/images/next-icon/next-icon-11.jpg",
                payload=Payload(
                    target_action="send_search_result",
                    keywords=keywords,
                    page=next_page,
                    subpage=1).get_content())
            quickreplies.add_quick_reply(next_button.get_content())

            if subpage == 1:
                send_api.send_text_message(f"👉 Résultats de recherche pour \"{keywords}\" :", recipient_id)
            send_api.send_text_message(f"Page {page} :", recipient_id)
            print(send_api.send_generic_message(
                elements.get_content(),
                recipient_id,
                quick_replies=quickreplies.get_content(),
                image_aspect_ratio="square"))

        return True


def add_to_cart(product_id, recipient_id):
    customer = customer_model.get_customer(recipient_id)
    try:
        customer_model.update_customer(
            customer_id=recipient_id,
            field="cart",
            new_value=customer.get("cart").extend({"product_id": product_id})
        )
    except Exception as e:
        send_api.send_text_message(
            f"❎ Une erreur est survenue lors de l'ajout au panier. {e}",
            recipient_id)
    else:
        send_api.send_text_message("Le produit a été ajouté au panier 🛒✅")


def remove_to_cart(product_id, recipient_id):
    customer = customer_model.get_customer(recipient_id)
    cart: list = customer["cart"]

    if len(cart) == 0:
        send_api.send_text_message("Ce produit n'est plus dans votre panier 🛒⛔")

    else:
        for idx, product in enumerate(cart.copy()):
            if product["product_id"] == product_id:
                cart.pop(idx)
                try:
                    customer_model.update_customer(
                        customer_id=recipient_id,
                        field="cart",
                        new_value=cart
                    )
                except Exception as e:
                    send_api.send_text_message(
                        f"❎ Une erreur est survenue lors de l'action effectué. {e}",
                        recipient_id)
                    return False
                else:
                    send_api.send_text_message("Le produit a été retiré du panier 🛒✅")
                    return True
        send_api.send_text_message(
            "⚠️ Il semblerait que ce produit a déjà été retiré du panier.",
            recipient_id)
        return False


def list_cart_products(recipient_id):
    pass


def clear_cart(recipient_id):
    customer = customer_model.get_customer(recipient_id)
    cart = customer["cart"]

    if len(cart) == 0:
        send_api.send_text_message("Votre panier est déjà vide.")
    
    else:
        try:
            customer_model.update_customer(
                customer_id=recipient_id,
                field="cart",
                new_value=[]
            )
        except Exception as e:
            send_api.send_text_message(
                f"❎ Une erreur est survenue lors de l'action effectué. {e}",
                recipient_id)
        else:
            send_api.send_text_message("Votre panier a été vidé avec succès 🛒✅")


# TODO : Devis
def show_estimated_price(recipient_id):
    pass


def get_currency(recipient_id):
    customer = customer_model.get_customer(recipient_id)
    
    send_api.send_text_message(
        f"La devise que vous utilisez actuellement est {CURRENCY_MAP.get(customer.get('currency'))}",
        recipient_id)


def ask_new_currency(recipient_id):
    quickreplies = msgr_api_components.QuickReplies()

    eur_currency_quickrep = msgr_api_components.QuickReply(
        "EUR",
        Payload(target_action="update_currency", currency="EUR").get_content(),
        image_url="https://www.pngall.com/wp-content/uploads/2018/05/Euro-Symbol-PNG-Clipart.png")
    quickreplies.add_quick_reply(eur_currency_quickrep.get_content())

    usd_currency_quickrep = msgr_api_components.QuickReply(
        "USD",
        Payload(target_action="update_currency", currency="USD").get_content(),
        image_url="https://www.freeiconspng.com/thumbs/dollar-icon-png/orange-coin-us-dollar-icon-8.png")
    quickreplies.add_quick_reply(usd_currency_quickrep.get_content())

    send_api.send_quick_replies(
        "💬 Quel devise voulez-vous utiliser ?",
        quickreplies.get_content(),
        recipient_id)


def update_currency(currency, recipient_id):
    try:
        customer_model.update_customer(
            customer_id=recipient_id,
            field="currency",
            new_value=currency
        )
    except Exception as e:
        send_api.send_text_message(
            f"Une erreur est survenue lors de la mise à jour de la devise. {e}",
            recipient_id)
    else:
        send_api.send_text_message(
            f"Vous utilisez maintenant {CURRENCY_MAP.get(currency)} comme devise.",
            recipient_id)


def show_exchange_rate(recipient_id):
    pass
