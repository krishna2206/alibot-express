import httpx
from bs4 import BeautifulSoup

URL = "https://www.bmoinet.net/"


def get_exchange_rate():
    response = httpx.get(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0"
        }
    )

    if response.status_code == 200:
        exchange_rate = {}
        soup = BeautifulSoup(response.text, features="lxml")
        er_block = soup.find("div", class_="cours_du_jour")
        for table_row in er_block.find("table").findAll("tr")[:-1]:
            currency_label = table_row.findAll("td")[0].text
            er_label = table_row.findAll("td")[1].text.replace(",", ".").replace(" ", "")
            if currency_label == "Euro":
                exchange_rate["EUR"] = float(er_label)
            elif currency_label == "DOLLAR (US)":
                exchange_rate["USD"] = float(er_label)
        return exchange_rate
    raise Exception(f"Failed to fetch HTML page. {response.status_code} {response.reason_phrase}")


if __name__ == "__main__":
    exchange_rate = get_exchange_rate()
    print(exchange_rate)
