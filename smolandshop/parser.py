from time import sleep

from bs4 import BeautifulSoup
from dotenv import load_dotenv
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
        item_name = ''.join(
            item for item in ' '.join(shop_item.text[:shop_item.text.rfind('г')].strip().split(' ')[:-1]))
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
        # print(f"\'{item_name}\'")
        # print(f"Название: {item_name}, Ссылка: {shop_item['href']}")
    return result


def process_tabaco(tabaco_link: TabacoLinksInShops):
    try:
        html = get_html(tabaco_link.link)
    except Exception as e:
        raise e
    parser = BeautifulSoup(html, "lxml")
    shop_product = parser.find("div", {"class": "shop-product js_shop"})
    shop_product_detail = shop_product.find("div", {"class": "shop-product__details"})
    details = dict()
    try:
        for detail in shop_product_detail.find("ul", {"class": "shop-product__properties"}).find_all("li", {
            "class": "shop-product__property"}):
            details[detail.text.split(":")[0]] = detail.text.split(":")[1].strip()
        tabaco = tabaco_link.tabaco
        Tabaco.update(
            country="" if details.get("Страна") is None else details.get("Страна"),
            taste="" if details.get("Вкус табака") is None else details.get("Вкус табака"),
            weight="" if details.get("Вес табака") is None else details.get("Вес табака"),
            krepost="" if details.get("Крепость табака") is None else details.get("Крепость табака"),
            cenovoy_segment="" if details.get("Ценовой сегмент табака") is None else details.get(
                "Ценовой сегмент табака"),
            dymnost="" if details.get("Дымность") is None else details.get("Дымность"),
            zharostoykost="" if details.get("Жаростойкость") is None else details.get("Жаростойкость"),
            stoykost_vkusa="" if details.get("Стойкость вкуса") is None else details.get("Стойкость вкуса"),
            sort_tabaka="" if details.get("Сорт табака") is None else details.get("Сорт табака"),
            taste_type="" if details.get("Тип вкуса") is None else details.get("Тип вкуса"),
            svezhest="" if details.get("Свежесть") is None else details.get("Свежесть"),
            sostav="" if details.get("Упаковка") is None else details.get("Упаковка"),
            upakovka="" if details.get("Состав") is None else details.get("Состав"),
            temp_hraneniya="" if details.get("Температура хранения") is None else details.get("Температура хранения"),
            srok_godnosti="" if details.get("Срок хранения") is None else details.get("Срок хранения"),
            english_name="" if details.get("Наименование англ.") is None else details.get("Наименование англ."),
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
    for i in range(2, last_page_number + 1):
        sleep(0.5)
        tabacos_links += get_items_from_page(shop, brand, brand_link + f"page{i}/")
    for tabaco_link in tabacos_links:
        sleep(0.5)
        process_tabaco(tabaco_link)


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
    # load_dotenv()
    initialize_db()
    parse_url(base_url)
    db.close()
