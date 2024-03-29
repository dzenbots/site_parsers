from time import sleep

from bs4 import BeautifulSoup
from requests import Session
from tqdm import tqdm

from exceptions import GetRequestException
from models import Shop, TabacoBrand, TabacoBrandAndShop, Tabaco, TabacoLinksInShops, initialize_db, db

base_url = "https://smolandshop.com/shop/tabak/"


def get_html(url: str):
    answer = None
    with Session() as session:
        try:
            responce = session.get(
                url=url
            )
        except Exception as e:
            raise e
        if responce.status_code == 200:
            answer = responce.text
        else:
            raise GetRequestException(message=f"Get response with code {responce.status_code} from {url}")
    return answer


def get_items_from_page(shop: Shop, brand: TabacoBrand, link: str) -> list[TabacoLinksInShops]:
    result: list[TabacoLinksInShops] = []
    try:
        html = get_html(link)
    except Exception as e:
        raise e
    parser = BeautifulSoup(html, "lxml")
    try:
        items = parser.find_all("li", {"class": "shop-item-product"})
    except Exception as e:
        raise e
    for item in items:
        try:
            shop_item = item.find("div", {"class": "shop-item-product__name"}).find("a")
        except Exception as e:
            raise e
        item_name = shop_item.text
        tabaco, created = Tabaco.get_or_create(
            tabaco_name=item_name,
            tabaco_brand=brand
        )
        tabaco_link_in_shop, created = TabacoLinksInShops.get_or_create(
            tabaco=tabaco,
            shop=shop,
            link=shop_item['href']
        )
        result.append(tabaco_link_in_shop)
        # print(f"Название: {item_name}, Ссылка: {shop_item['href']}")
    return result


def process_tabaco(tabaco_link: TabacoLinksInShops):
    # print(f"{tabaco_link.tabaco.tabaco_name} {tabaco_link.link}")
    try:
        html = get_html(tabaco_link.link)
    except Exception as e:
        raise e
    parser = BeautifulSoup(html, "lxml")
    try:
        shop_product = parser.find("div", {"class": "shop-product js_shop"})
        # print("shop_product")
        shop_product_detail = shop_product.find("div", {"class": "shop-product__details"})
        # print("shop_product_detail")
        details = dict()
        for detail in shop_product_detail.find("ul", {"class": "shop-product__properties"}).find_all("li", {"class": "shop-product__property"}):
            details[detail.text.split(":")[0]] = detail.text.split(":")[1].strip()
        # print(details)
        tabaco = tabaco_link.tabaco
        Tabaco.update(
            country=details["Страна"],
            taste=details["Вкус табака"],
            weight=details["Вес табака"],
            krepost=details["Крепость табака"],
            cenovoy_segment=details["Ценовой сегмент табака"],
            dymnost=details["Дымность"],
            zharostoykost=details["Жаростойкость"],
            stoykost_vkusa=details["Стойкость вкуса"],
            sort_tabaka=details["Сорт табака"],
            taste_type=details["Тип вкуса"],
            svezhest=details["Свежесть"],
            sostav=details["Упаковка"],
            upakovka=details["Состав"],
            temp_hraneniya=details["Температура хранения"],
            srok_godnosti=details["Срок хранения"],
            english_name=details["Наименование англ."],
        ).where(Tabaco.id == tabaco.id).execute()
    except:
        ...


def process_brand(shop: Shop, brand: TabacoBrand, brand_link: str):
    tabacos_links: list[TabacoLinksInShops] = []
    try:
        html = get_html(brand_link)
    except Exception as e:
        raise e
    parser = BeautifulSoup(html, "lxml")
    try:
        pages = parser.find("ul", {"class": "pagination paginator"})
        last_page = pages.find_all("li")[-2]
        last_page_text = last_page.find("a").text
        if last_page_text == "...":
            last_page_number = int(last_page.find("a")["title"].split(" ")[-1])
        else:
            last_page_number = int(last_page_text)
    except:
        last_page_number = 0
    tabacos_links += get_items_from_page(shop, brand, brand_link)
    sleep(2)
    for i in range(2, last_page_number + 1):
        sleep(2)
        tabacos_links += get_items_from_page(shop, brand, brand_link + f"page{i}/")
    for tabaco_link in tabacos_links:
        process_tabaco(tabaco_link)
        sleep(0.5)


def parse_url(url: str):
    shop, created = Shop.get_or_create(
        shop_name="SmolandShop",
        shop_link="https://smolandshop.com/shop/tabak/"
    )
    try:
        html = get_html(shop.shop_link)
    except Exception as e:
        raise e
    parser = BeautifulSoup(html, "lxml")
    try:
        categories = parser.find("div", {"class": "shop-block-categories"}).find_all("div", {"class": "h2"})
    except Exception as e:
        raise e
    for i in tqdm(range(0, len(categories)), desc=shop.shop_name):
        category = categories[i]
        try:
            inner = category.find("a")
        except Exception as e:
            raise e
        tabaco_brand_name = inner.text.rstrip(" для кальяна")[6:]
        tabaco_brand_link = inner['href']
        brand, created = TabacoBrand.get_or_create(
            brand_name=tabaco_brand_name
        )
        TabacoBrandAndShop.get_or_create(
            brand=brand,
            shop=shop
        )
        process_brand(
            shop=shop,
            brand=brand,
            brand_link=tabaco_brand_link
        )
        # print(f"{tabaco_brand_name} --- {tabaco_brand_link}")


if __name__ == "__main__":
    initialize_db()
    parse_url(base_url)
    db.close()
