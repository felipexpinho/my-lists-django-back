import requests
from bs4 import BeautifulSoup
import json

import sys

sys.stdout.reconfigure(encoding="utf-8")  # Force UTF-8 output


def get_product_info_from_url(url: str) -> dict | str:
    try:
        if "nike" in url:
            try:
                return get_product_from_nike(url)
            except:
                return "Could not find store data"
        elif "adidas" in url:
            try:
                return get_product_from_adidas(url)
            except:
                return "Could not find store data"

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"
        }

        html = requests.get(url, headers=headers).content
        soup = BeautifulSoup(html, "lxml")

        data = soup.find_all("script", type="application/ld+json")
        content_store = data[0].get_text()
        try:
            if "kabum" in content_store:
                return get_product_from_kabum(soup, url)
            return "Could not find product data"
        except:
            return "Could not find product data"
    except:
        return "Could not find store data"


# def get_product_from_nike(soup, url: str) -> dict | str:
#     try:
#         data = soup.find("script", id="__NEXT_DATA__", type="application/json")
#         content = data.get_text()
#         json_object = json.loads(content)

#         result = {}

#         result["name"] = (
#             json_object["props"]["pageProps"]["product"]["name"]
#             + " "
#             + json_object["props"]["pageProps"]["product"]["nickname"]
#         )
#         result["price"] = json_object["props"]["pageProps"]["product"]["installments"][
#             0
#         ]["value"]
#         result["category"] = json_object["props"]["pageProps"]["product"]["category"]
#         result["sub_group"] = json_object["props"]["pageProps"]["product"]["subGroup"]
#         result["is_available"] = json_object["props"]["pageProps"]["product"][
#             "isAvailable"
#         ]
#         result["link"] = url
#         result["photo"] = (
#             f'https://imgnike-a.akamaihd.net/{json_object["props"]["pageProps"]["product"]["photos"]["sizes"][-1]}/{json_object["props"]["pageProps"]["product"]["selectedProduct"]}.jpg'
#         )
#         result["store"] = "Nike"
#         result["store_url"] = "https://www.nike.com.br"

#         return result
#     except Exception as e:
#         return f"Search failed at: {url}"


def get_product_from_nike(url: str) -> dict | str:
    try:
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Referer": "https://www.nike.com.br/",
                "Accept-Language": "pt-BR,pt;q=0.9,en-US,en;q=0.8",
            }
        )

        # Visit homepage first to get cookies
        session.get("https://www.nike.com.br")

        # Fetch the product page
        response = session.get(url)

        if response.status_code != 200:
            return f"Access Denied or Page Not Found: {url}"

        # response.encoding = "latin1"

        # Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Find product data inside <script> tag
        data = soup.find("script", id="__NEXT_DATA__", type="application/json")
        if not data:
            return f"Product data not found at: {url}"

        content = data.get_text()
        json_object = json.loads(content)

        # Extract product details
        product_info = json_object["props"]["pageProps"]["product"]

        result = {
            "name": f'{product_info["name"]} {product_info["nickname"]}',
            "price": product_info["installments"][0]["value"],
            "category": product_info["category"],
            "sub_group": product_info["subGroup"],
            "is_available": product_info["isAvailable"],
            "link": url,
            "photo": f'https://imgnike-a.akamaihd.net/{product_info["photos"]["sizes"][-1]}/{product_info["selectedProduct"]}.jpg',
            "store": "Nike",
            "store_url": "https://www.nike.com.br",
        }

        return result

    except Exception as e:
        return f"Error fetching product data from: {url} | Error: {str(e)}"


def get_product_from_adidas(url: str) -> dict | str:
    try:
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Referer": "https://www.adidas.com.br/",
                "Accept-Language": "pt-BR,pt;q=0.9,en-US,en;q=0.8",
            }
        )

        # Visit homepage first to get cookies
        session.get("https://www.adidas.com.br")

        # Fetch the product page
        response = session.get(url)

        if response.status_code != 200:
            return f"Access Denied or Page Not Found: {url}"

        # print(response.text.encode("utf-8", "ignore").decode("utf-8"))

        # Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Find product data inside <script> tag
        data = soup.find("script", type="application/ld+json")
        if not data:
            return f"Product data not found at: {url}"

        content = data.get_text()

        # Ensure valid UTF-8 encoding before loading JSON
        content = content.encode("utf-8", "ignore").decode("utf-8")

        json_object = json.loads(content)

        # Extract product details
        product_info = json_object

        result = {
            "name": product_info["name"],
            "price": product_info["offers"]["price"],
            "category": product_info["category"],
            "sub_group": product_info["category"],
            "is_available": product_info["offers"]["availability"] == "InStock",
            "link": url,
            "photo": product_info["image"][0],
            "store": "Adidas",
            "store_url": "https://www.adidas.com.br",
        }

        return result

    except Exception as e:
        return f"Error fetching product data from: {url} | Error: {str(e)}"


def get_product_from_kabum(soup, url: str) -> dict | str:
    try:
        data = soup.find("script", id="__NEXT_DATA__", type="application/json")
        content = data.get_text()
        json_object = json.loads(content)

        result = {}

        result["name"] = json_object["props"]["pageProps"]["initialZustandState"][
            "descriptionProduct"
        ]["name"]
        result["price"] = json_object["props"]["pageProps"]["initialZustandState"][
            "descriptionProduct"
        ]["priceDetails"]["discountPrice"]
        result["category"] = json_object["props"]["pageProps"]["initialZustandState"][
            "descriptionProduct"
        ]["menus"][0]["name"]
        result["sub_group"] = json_object["props"]["pageProps"]["initialZustandState"][
            "descriptionProduct"
        ]["menus"][1]["name"]
        result["is_available"] = json_object["props"]["pageProps"][
            "initialZustandState"
        ]["descriptionProduct"]["available"]
        result["link"] = url
        result["photo"] = json_object["props"]["pageProps"]["initialZustandState"][
            "descriptionProduct"
        ]["photos"][0]
        result["store"] = "Kabum"
        result["store_url"] = "https://www.kabum.com.br"

        return result
    except Exception as e:
        return f"Search failed at: {url}"


# ----------------------------------------------------------------


def test1():
    url = "https://www.kabum.com.br/produto/380745/ssd-1-tb-kingston-nv2-m-2-2280-pcie-nvme-leitura-3500-mb-s-e-gravacao-2100-mb-s-snv2s-1000g"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        try:
            # Encontrar o script com id "__NEXT_DATA__" e tipo "application/json"
            start_index = response.text.find(
                '<script id="__NEXT_DATA__" type="application/json">'
            ) + len('<script id="__NEXT_DATA__" type="application/json">')
            end_index = response.text.find("</script>", start_index)
            json_data = response.text[start_index:end_index]

            # Carregar o conteúdo JSON
            json_object = json.loads(json_data)

            # Aqui você pode acessar os dados diretamente do json_object
            # print(json_object)

            result = {}

            result["name"] = json.loads(
                json_object["props"]["pageProps"]["data"]["productCatalog"]
            )["name"]
            result["price"] = float(
                json.loads(json_object["props"]["pageProps"]["data"]["productCatalog"])[
                    "offer"
                ]["priceWithDiscount"]
            )
            result["category"] = str(
                json.loads(json_object["props"]["pageProps"]["data"]["productCatalog"])[
                    "category"
                ]
            ).split("/")[0]
            result["sub_group"] = str(
                json.loads(json_object["props"]["pageProps"]["data"]["productCatalog"])[
                    "category"
                ]
            ).split("/")[1]
            result["is_available"] = json.loads(
                json_object["props"]["pageProps"]["data"]["productCatalog"]
            )["available"]
            result["link"] = url
            result["photo"] = json.loads(
                json_object["props"]["pageProps"]["data"]["productCatalog"]
            )["photos"]["g"][0]
            result["store"] = "Kabum"
            result["store_url"] = "https://www.kabum.com"

            # print(result)
            return result
        except Exception as e:
            print(f"Erro ao acessar os dados JSON: {e}")
    else:
        print(f"Erro ao acessar a página: Status code {response.status_code}")
