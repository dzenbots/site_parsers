import traceback

from bs4 import BeautifulSoup
from requests import Session
from tqdm import tqdm

base_url = "https://smolandshop.com/shop/tabak/"


def get_html(url: str):
    answer = None
    with Session() as session:
        responce = session.get(
            url=url
        )
        if responce.status_code == 200:
            answer = responce.text
        else:
            raise Exception()
    return answer


def get_items_from_page(link: str):
    html = get_html(link)
    parser = BeautifulSoup(html, "lxml")
    items = parser.find_all("li", {"class": "shop-item-product"})
    for item in items:
        shop_item = item.find("div", {"class": "shop-item-product__name"}).find("a")
        if shop_item.text[-1] == " ":
            shop_item.text[-1] = "1"
        print(f"\'{shop_item.text}\'")
        item_name = " ".join(f"{i}" for i in shop_item.text.split(" ")[:-2])
        print(f"Название: {item_name}, Ссылка: {shop_item['href']}")


def process_brand(brand_name: str, brand_link: str):
    html = get_html(brand_link)
    parser = BeautifulSoup(html, "lxml")
    pages = parser.find("ul", {"class": "pagination paginator"})
    last_page = pages.find_all("li")[-2]
    last_page_text = last_page.find("a").text
    last_page_number = 0
    if last_page_text == "...":
        last_page_number = int(last_page.find("a")["title"].split(" ")[-1])
    else:
        last_page_number = int(last_page_text)
    get_items_from_page(brand_link)
    for i in range(2, last_page_number + 1):
        get_items_from_page(brand_link + f"page{i}/")


def parse_url(url: str):
    html = get_html(url)
    # with open('test.html', 'w') as file:
    #     file.write(html)
    parser = BeautifulSoup(html, "lxml")
    categories = parser.find("div", {"class": "shop-block-categories"}).find_all("div", {"class": "h2"})
    # for category in categories:
    for i in tqdm(range(0, len(categories)), desc=url):
        category = categories[i]
        inner = category.find("a")
        tabaco_brand_name = inner.text.rstrip(" для кальяна")[6:]
        tabaco_brand_link = inner['href']
        process_brand(brand_name=tabaco_brand_name, brand_link=tabaco_brand_link)
        # print(f"{tabaco_brand_name} --- {tabaco_brand_link}")


if __name__ == "__main__":
    try:
        parse_url(base_url)
    except Exception as e:
        traceback.print_exc()
