import re


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
            except (KeyError, TypeError):
                return None
        return value