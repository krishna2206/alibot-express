from datetime import datetime

import pytz
from split import chop
from fancify_text import bold, italic

from chatbot.utils import Payload
from chatbot.sharedinstances import send_api, msgr_api_components, user_model

from .core import logic
from .core.config import LOCALE, REGION, SITE
from .core.customermodel import CustomerModel
from .core.dependencies import bmoi_er
from .core.dependencies.aliexpress import AliExpress

from chatbot.packages.common.common import safe_execute_action

customer_model = CustomerModel()
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


@safe_execute_action
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


@safe_execute_action
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


def ask_quantity_to_add(product_id: str, variant_id: str, max_quantity: int, recipient_id: str):
    user_model.add_query(
        recipient_id,
        "add_to_cart",
        product_id=product_id,
        variant_id=variant_id,
        max_quantity=max_quantity)

    send_api.send_text_message("💬 Combien d'unité voulez-vous ajouter au panier ?", recipient_id)


@safe_execute_action
def add_to_cart(quantity: int, product_id: str, variant_id: str, max_quantity: int, recipient_id: str):
    try:
        quantity = int(quantity)
    except ValueError:
        send_api.send_text_message("⛔ Le nombre que vous avez entré est incorrect.", recipient_id)
        ask_quantity_to_add(product_id, variant_id, max_quantity, recipient_id)
    else:
        if quantity <= 0:
            send_api.send_text_message(
                "⛔ Le nombre que vous avez entré ne doit pas être négatif ou nul.", recipient_id)
            ask_quantity_to_add(product_id, variant_id, max_quantity, recipient_id)

        elif quantity > max_quantity:
            send_api.send_text_message(
                "⛔ Le nombre que vous avez entré ne doit pas dépasser la quantité disponible.", recipient_id)
            ask_quantity_to_add(product_id, variant_id, max_quantity, recipient_id)

        else:
            customer = customer_model.get_customer(recipient_id)
            cart: list = customer.get("cart")
            product_already_exists = logic._check_cart_product(product_id, cart)

            if product_already_exists:
                send_api.send_text_message("Ce produit existe déjà dans le panier.", recipient_id)

            else:
                try:
                    cart.append({"product_id": product_id, "variant_id": variant_id, "quantity": quantity})
                    customer_model.update_customer(
                        customer_id=recipient_id,
                        cart=cart
                    )
                except Exception as e:
                    send_api.send_text_message(
                        f"❎ Une erreur est survenue lors de l'ajout au panier. {e}",
                        recipient_id)
                else:
                    send_api.send_text_message("Le produit a été ajouté au panier 🛒✅", recipient_id)


@safe_execute_action
def remove_to_cart(product_id: str, recipient_id: str):
    customer = customer_model.get_customer(recipient_id)
    cart: list = customer["cart"]

    if len(cart) == 0:
        send_api.send_text_message("Votre panier est déjà vide 🛒⛔", recipient_id)

    else:
        product_still_exists = logic._check_cart_product(product_id, cart)

        if product_still_exists:
            for idx, product in enumerate(cart.copy()):
                if product["product_id"] == product_id:
                    cart.pop(idx)
                    try:
                        customer_model.update_customer(
                            customer_id=recipient_id,
                            cart=cart
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


@safe_execute_action
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
            image_url="https://cdn-icons-png.flaticon.com/512/1213/1213930.png",
            payload=Payload(
                target_action="show_estimated_price").get_content())
        quickreplies.add_quick_reply(show_estimated_price_button.get_content())

        # ? Clear cart button
        clear_cart_button = msgr_api_components.QuickReply(
            title="Vider le panier",
            image_url="https://cdn-icons-png.flaticon.com/512/2038/2038854.png",
            payload=Payload(
                target_action="clear_cart").get_content())
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


@safe_execute_action
def clear_cart(recipient_id: str):
    customer = customer_model.get_customer(recipient_id)
    cart = customer["cart"]

    if len(cart) == 0:
        send_api.send_text_message("Votre panier est déjà vide.", recipient_id)
    
    else:
        try:
            customer_model.update_customer(
                customer_id=recipient_id,
                cart=[]
            )
        except Exception as e:
            send_api.send_text_message(
                f"❎ Une erreur est survenue lors de l'action effectué. {e}",
                recipient_id)
        else:
            send_api.send_text_message("Votre panier a été vidé avec succès 🛒✅", recipient_id)


@safe_execute_action
def show_estimated_price(recipient_id: str):
    customer = customer_model.get_customer(recipient_id)
    cart = customer["cart"]
    display_currency = "€" if customer.get("currency") == "EUR" else "$"
    aliexpress = AliExpress(
        REGION, customer.get("currency"), LOCALE, SITE)
    exchange_rate = bmoi_er.get_exchange_rate()

    estimated_price_msg = "🛒 Voici le devis de votre panier :\n\n"
    total_price = 0
    for cart_product in cart:
        product = aliexpress.get_product(cart_product["product_id"])

        if cart_product["variant_id"] is not None:
            variant = logic._get_product_variant(cart_product["variant_id"], product["prices"])
        else:
            variant = product["prices"][0]

        if product["shippingFee"] is not None:
            curr_total_price = (variant["promotionalPrice"] * cart_product["quantity"]) + product["shippingFee"]
        else:
            curr_total_price = variant["promotionalPrice"] * cart_product["quantity"]

        total_price += curr_total_price
        
        estimated_price_msg += bold(f"• {product['title']} ({variant['variantName']}) :\n")
        estimated_price_msg += f" 💰 Prix unitaire : {variant['promotionalPrice']} {display_currency}\n"
        estimated_price_msg += f" 🛍 Quantité : {cart_product['quantity']}\n"
        estimated_price_msg += f" 💰 Prix total : {round(variant['promotionalPrice'] * cart_product['quantity'], 1)} {display_currency}\n"
        if product['shippingFee'] is not None:
            estimated_price_msg += f" 🚛 Frais de livraison : {product['shippingFee']} {display_currency}\n"
        if (product['deliveryDetails']['deliveryDayMin'] is not None) and (product['deliveryDetails']['deliveryDayMax'] is not None):
            estimated_price_msg += f" 🚚 Durée estimée de livraison : {product['deliveryDetails']['deliveryDayMin']} - {product['deliveryDetails']['deliveryDayMax']} jours"
        
        if cart_product != cart[-1]:
            estimated_price_msg += "\n\n"

    total_price = round(total_price, 1)
    total_price_ariary = round(total_price * exchange_rate.get(customer.get('currency')), 1)
    estimated_price_msg += (
        bold(f"\n\n🛒 Prix total du panier :\n") +
        f"{total_price} {display_currency} soit {total_price_ariary} Ariary\n")

    send_api.send_text_message(estimated_price_msg, recipient_id)


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


@safe_execute_action
def update_currency(currency: str, recipient_id: str):
    try:
        customer_model.update_customer(
            customer_id=recipient_id,
            currency=currency
        )
    except Exception as e:
        send_api.send_text_message(
            f"Une erreur est survenue lors de la mise à jour de la devise. {e}",
            recipient_id)
    else:
        send_api.send_text_message(
            f"✅ Vous utilisez maintenant {CURRENCY_MAP.get(currency)} comme devise.",
            recipient_id)


@safe_execute_action
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
