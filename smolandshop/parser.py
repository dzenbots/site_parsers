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


def parse_url(url: str):
    html = None
    try:
        html = get_html(url)
        with open('test.html', 'w') as file:
            file.write(html)
            parser = BeautifulSoup(html, "lxml")
            rezult = parser.find("div", {"class": "shop-block-categories"}).find_all("a")
            for item in rezult:
                print(f"{item.text} {item['href']}")
    except Exception as e:
        ...


if __name__ == "__main__":
    parse_url(base_url)
