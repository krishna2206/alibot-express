from chatbot.packages.myself.aliexpress import (
    add_to_cart, ask_new_currency, ask_product_keyword, clear_cart,
    get_currency, list_cart_products, list_product_variants, remove_to_cart, send_search_result,
    show_estimated_price, show_exchange_rate, update_currency)
from chatbot.packages.myself.myself import help_message, welcome_message


INTENTS = [
    {
        "name": "welcome_message",
        "action": welcome_message
    },
    {
        "type": "fallback",
        "name": "help_message",
        "action": help_message
    },
    {
        "name": "ask_product_keyword",
        "action": ask_product_keyword
    },
    {
        "name": "send_search_result",
        "action": send_search_result
    },
    {
        "name": "list_product_variants",
        "action": list_product_variants
    },
    {
        "name": "add_to_cart",
        "action": add_to_cart
    },
    {
        "name": "remove_to_cart",
        "action": remove_to_cart
    },
    {
        "name": "list_cart_products",
        "action": list_cart_products
    },
    {
        "name": "clear_cart",
        "action": clear_cart
    },
    {
        "name": "show_estimated_price",
        "action": show_estimated_price
    },
    {
        "name": "get_currency",
        "action": get_currency
    },
    {
        "name": "ask_new_currency",
        "action": ask_new_currency
    },
    {
        "name": "update_currency",
        "action": update_currency
    },
    {
        "name": "show_exchange_rate",
        "action": show_exchange_rate
    }
    
]
