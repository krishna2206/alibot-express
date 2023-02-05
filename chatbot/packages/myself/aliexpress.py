from datetime import datetime

import pytz
from split import chop

import config
from chatbot.utils import Payload
from chatbot.sharedinstances import send_api, msgr_api_components, user_model

from .core import logic
from .core.config import LOCALE, REGION, SITE
from .core.customermodel import CustomerModel
from .core.dependencies import bmoi_er
from .core.dependencies.aliexpress import AliExpress

customer_model = CustomerModel(config)
CURRENCY_MAP = {
    "EUR": "l'Euro",
    "USD": "le Dollar USD"
}


def ask_product_keyword(recipient_id: str):
    user_model.add_query(
        recipient_id,
        "send_search_result",
        page=1,
        subpage=1)

    send_api.send_text_message("💬 Quel produit voulez-vous rechercher ?", recipient_id)


def send_search_result(keywords: str, page: int, subpage: int, recipient_id: str):
    customer = customer_model.get_customer(recipient_id)
    aliexpress = AliExpress(
        REGION, customer.get("currency"), LOCALE, SITE)
    search_results = aliexpress.search_product(keywords, page)["results"]

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

        elements = logic.create_product_elements(current_page_list, customer_id=recipient_id)
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


def list_product_variants(product_id: str, page: int, recipient_id: str):
    customer = customer_model.get_customer(recipient_id)
    aliexpress = AliExpress(
        REGION, customer.get("currency"), LOCALE, SITE)
    product = aliexpress.get_product(product_id)
    product_variants = product["prices"]

    splitted_product_variants = list(chop(10, product_variants))
    if len(product_variants) > 10:
        current_page_list = splitted_product_variants[page - 1]
    else:
        current_page_list = product_variants

    elements = logic.create_product_variant_elements(
        current_page_list, customer_id=recipient_id, product_id=product_id)
    quickreplies = msgr_api_components.QuickReplies()

    # ? Reiterate action button
    reiterate_button = msgr_api_components.QuickReply(
        title="Autre recherche",
        image_url="https://freeiconshop.com/wp-content/uploads/edd/refresh-flat.png",
        payload=Payload(
            target_action="ask_product_keyword").get_content())
    quickreplies.add_quick_reply(reiterate_button.get_content())

    #* Fin de la page
    if current_page_list == splitted_product_variants[-1]:
        send_api.send_text_message(f"🌈 Voici les variantes de ce produit :", recipient_id)
        print(send_api.send_generic_message(
            elements.get_content(),
            recipient_id,
            quick_replies=quickreplies.get_content(),
            image_aspect_ratio="square"))

    else:
        next_page = page + 1
        next_button = msgr_api_components.QuickReply(
            title="Suivant",
            image_url="https://icon-library.com/images/next-icon/next-icon-11.jpg",
            payload=Payload(
                target_action="list_product_variants",
                product_id=product_id,
                page=next_page).get_content())
        quickreplies.add_quick_reply(next_button.get_content())

        if page == 1:
            send_api.send_text_message(f"🌈 Voici les variantes de ce produit :", recipient_id)
        send_api.send_text_message(f"Page {page} :", recipient_id)
        print(send_api.send_generic_message(
            elements.get_content(),
            recipient_id,
            quick_replies=quickreplies.get_content(),
            image_aspect_ratio="square"))

    return True
    

# TODO : To test
def add_to_cart(product_id: str, variant_id: str, recipient_id: str):
    customer = customer_model.get_customer(recipient_id)
    cart = customer.get("cart")
    product_already_exists = logic._check_cart_product(product_id, cart)

    if product_already_exists:
        send_api.send_text_message("Ce produit existe déjà dans le panier.", recipient_id)

    else:
        try:
            customer_model.update_customer(
                customer_id=recipient_id,
                field="cart",
                new_value=customer.get("cart").extend({"product_id": product_id, "variant_id": variant_id})
            )
        except Exception as e:
            send_api.send_text_message(
                f"❎ Une erreur est survenue lors de l'ajout au panier. {e}",
                recipient_id)
        else:
            send_api.send_text_message("Le produit a été ajouté au panier 🛒✅", recipient_id)


# TODO : To test
def remove_to_cart(product_id: str, recipient_id: str):
    customer = customer_model.get_customer(recipient_id)
    cart: list = customer["cart"]

    if len(cart) == 0:
        send_api.send_text_message("Votre panier est déjà vide 🛒⛔")

    else:
        product_still_exists = logic._check_cart_product(product_id, cart)

        if product_still_exists:
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
                    else:
                        send_api.send_text_message("Le produit a été retiré du panier 🛒✅", recipient_id)
        
        else:
            send_api.send_text_message(
                "⚠️ Il semblerait que ce produit a déjà été retiré du panier.",
                recipient_id)


# TODO : To test
def list_cart_products(page: int, recipient_id: str):
    customer = customer_model.get_customer(recipient_id)
    cart = customer["cart"]

    if len(cart) == 0:
        send_api.send_text_message(
            "Vous n'avez pas encore de produits dans votre panier.",
            recipient_id)

    else:
        splitted_cart = list(chop(10, cart))
        if len(cart) > 10:
            current_page_list = splitted_cart[page - 1]
        else:
            current_page_list = cart

        elements = logic.create_cart_product_elements(current_page_list, customer_id=recipient_id)
        quickreplies = msgr_api_components.QuickReplies()

        # ? Ask estimate button
        show_estimated_price_button = msgr_api_components.QuickReply(
            title="Demander devis",
            image_url="https://cdn-icons-png.flaticon.com/512/712/712613.png",
            payload=Payload(
                target_action="show_estimated_price").get_content())
        quickreplies.add_quick_reply(show_estimated_price_button.get_content())

        # ? Clear cart button
        clear_cart_button = msgr_api_components.QuickReply(
            title="Vider le panier",
            image_url="https://cdn-icons-png.flaticon.com/512/2038/2038854.png",
            payload=Payload(
                target_action="clear_cart_button").get_content())
        quickreplies.add_quick_reply(clear_cart_button.get_content())

        #* Fin de la page
        if current_page_list == splitted_cart[-1]:
            send_api.send_text_message(f"🛒 Voici les produits dans votre panier :", recipient_id)
            print(send_api.send_generic_message(
                elements.get_content(),
                recipient_id,
                quick_replies=quickreplies.get_content(),
                image_aspect_ratio="square"))

        else:
            next_page = page + 1
            next_button = msgr_api_components.QuickReply(
                title="Suivant",
                image_url="https://icon-library.com/images/next-icon/next-icon-11.jpg",
                payload=Payload(
                    target_action="list_cart_products",
                    page=next_page).get_content())
            quickreplies.add_quick_reply(next_button.get_content())

            if page == 1:
                send_api.send_text_message(f"🛒 Voici les produits dans votre panier :", recipient_id)
            send_api.send_text_message(f"Page {page} :", recipient_id)
            print(send_api.send_generic_message(
                elements.get_content(),
                recipient_id,
                quick_replies=quickreplies.get_content(),
                image_aspect_ratio="square"))

        return True


# TODO : To test
def clear_cart(recipient_id: str):
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
def show_estimated_price(recipient_id: str):
    pass


def get_currency(recipient_id: str):
    customer = customer_model.get_customer(recipient_id)
    
    send_api.send_text_message(
        f"🪙 La devise que vous utilisez actuellement est {CURRENCY_MAP.get(customer.get('currency'))}",
        recipient_id)


def ask_new_currency(recipient_id: str):
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


def update_currency(currency: str, recipient_id: str):
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
            f"✅ Vous utilisez maintenant {CURRENCY_MAP.get(currency)} comme devise.",
            recipient_id)


def show_exchange_rate(recipient_id: str):
    TIMEZONE_MG = pytz.timezone("Indian/Antananarivo")
    exchange_rate = bmoi_er.get_exchange_rate()
    exchange_rate_msg = (
        f"📈 Taux de change du {datetime.now(TIMEZONE_MG).strftime('%d/%m/%Y')} à {datetime.now(TIMEZONE_MG).strftime('%H:%M')} :\n\n" +
        f"1 € = {exchange_rate.get('EUR')} Ariary\n" +
        f"1 $ = {exchange_rate.get('USD')} Ariary")
    send_api.send_text_message(
        exchange_rate_msg,
        recipient_id)
