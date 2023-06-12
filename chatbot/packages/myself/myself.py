import random

from chatbot.utils import Payload
from chatbot.sharedinstances import send_api, msgr_api_components

WELCOME_MESSAGES = (
    "Bienvenue dans notre chatbot! Vous pouvez désormais trouver facilement et rapidement les produits sur Aliexpress et recevoir des devis en temps réel sans vous soucier du taux de change.",
    "Bonjour! Vous pouvez maintenant effectuer des recherches sur Aliexpress sans vous soucier du taux de change et recevoir des devis en un clin d'œil grâce à notre chatbot.",
    "Bonjour et bienvenue! Notre chatbot vous facilite la recherche de produits sur Aliexpress avec des devis en temps réel sans vous soucier du taux de change.",
    "Salutations! Grâce à notre chatbot, trouver des produits sur Aliexpress est plus facile que jamais avec des devis immédiats, sans les complications du taux de change."
)


def welcome_message(recipient_id):
    send_api.send_text_message(random.choice(WELCOME_MESSAGES), recipient_id)
    __ask_currency(recipient_id)


def __ask_currency(recipient_id):
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
        "Pour commencer, quel devise voulez-vous utiliser 🤔 ?",
        quickreplies.get_content(),
        recipient_id)


def help_message(recipient_id):
    help_text = (
        "Voici quelques astuces pour utiliser notre chatbot:\n"
        "- Pour rechercher des produits, utilisez le bouton 🔎 Rechercher des produits.\n"
        "- Pour voir votre panier, appuyez sur le bouton 🛒 Mon panier.\n"
        "- Pour vérifier ou changer de devise, utilisez les boutons 🪙 Ma devise et 🪙 Changer de devise.\n"
        "- Pour consulter le taux de change, appuyez sur le bouton 💱 Taux de change.\n"
        "Si vous avez besoin d'aide supplémentaire, n'hésitez pas à nous envoyer un message."
    )
    send_api.send_text_message(help_text, recipient_id)

