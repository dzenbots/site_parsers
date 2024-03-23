from bs4 import BeautifulSoup
from requests import Session

base_url = "https://smolandshop.com/shop/tabak/"


def get_html(url: str):
    answer = None
    with Session() as session:
        try:
            responce = session.get(
                url=url
            )
            if responce.status_code == 200:
                answer = responce.text
            else:
                raise Exception()
        except Exception as e:
            raise e
    return answer


def process_brand(brand_name: str, brand_link: str):
    html = get_html(brand_link)
    parser = BeautifulSoup(html, "lxml")
    try:
        pages = parser.find("ul", {"class": "pagination paginator"})
        last_page = pages.find_all("li")[-2]
        try:
            last_page_text = last_page.find("a").text
            if last_page_text == "...":
                last_page_number = int(last_page.find("a")["title"].split(" ")[-1])
            else:
                last_page_number = int(last_page_text)
        except:
            last_page_number = 0
    except:
        last_page_number = 0
    print(last_page_number)


def parse_url(url: str):
    try:
        html = get_html(url)
        with open('test.html', 'w') as file:
            file.write(html)
            parser = BeautifulSoup(html, "lxml")
            categories = parser.find("div", {"class": "shop-block-categories"}).find_all("div", {"class": "h2"})
            for category in categories:
                inner = category.find("a")
                tabaco_brand_name = inner.text.rstrip(" для кальяна")[6:]
                tabaco_brand_link = inner['href']
                process_brand(brand_name=tabaco_brand_name, brand_link=tabaco_brand_link)
                print(f"{tabaco_brand_name} --- {tabaco_brand_link}")
                #

    except Exception as e:
        raise e


if __name__ == "__main__":
    parse_url(base_url)
