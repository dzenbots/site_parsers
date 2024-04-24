import asyncio

import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from models import initialize_db, close_db, Shop, ShopItemCategory, ShopItemCategoryBrand, BrandItem

base_url: str = "https://smolandshop.com"


class SmolandshopParser:

    async def parse_website(self, session: aiohttp.ClientSession):
        shop, created = Shop.get_or_create(
            shop_name="Smolandshop",
            shop_link=base_url
        )
        try:
            async with session.get(base_url) as resp:
                if resp.status != 200:
                    raise Exception()
                html = await resp.text()
                try:
                    parser = BeautifulSoup(html, features="lxml")
                except:
                    print(f"Unable to parse {base_url}")
                    return
        except:
            print(f"Unable to connect to {self.base_url}")
            return
        try:
            shop_item_categories = parser.find(
                name="nav",
                attrs={
                    'class': 'navigation-block__menu navigation'
                }
            ).find_all(
                name='li',
                attrs={
                    'class': 'navigation__item navigation__item_main navigation__item_parent'
                }
            )
        except:
            print(f"Unable to find shop item categories in {base_url}")
            return
        for category in shop_item_categories:
            try:
                ShopItemCategory.get_or_create(
                    category_name=category.find('a').text,
                    category_link=category.find('a')['href'],
                    shop=shop
                )
            except:
                print(f"Unable to parse category")
        await self.process_categories(session=session)

    async def process_categories(self, session: aiohttp.ClientSession):
        for category in ShopItemCategory.select():
            async with session.get(category.category_link) as resp:
                try:
                    parser = BeautifulSoup(await resp.text(), features="lxml")
                except:
                    print(f"Unable to get brands from {category.category_link}")
                    return
            try:
                brands = parser.find(name='div', attrs={'class': 'shop-block-categories'}).find_all(
                    name='div',
                    attrs={
                        'class': 'h2'
                    }
                )
            except:
                print(f"Unable to get brands from {category.category_link}")
                return
            for brand in brands:
                ShopItemCategoryBrand.get_or_create(
                    brand_name=brand.find(name='a').text,
                    brand_link=brand.find(name='a')['href'],
                    category=category
                )
        await self.proccess_brands(session=session)

    async def proccess_brands(self, session: aiohttp.ClientSession):
        for brand in ShopItemCategoryBrand.select():
            async with session.get(brand.brand_link) as resp:
                try:
                    parser = BeautifulSoup(await resp.text(), features="lxml")
                except:
                    print(f"Unable to parse brand {brand.brand_name}")
                    return
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
            for i in range(1, last_page_number + 1):
                await asyncio.sleep(1)
                await self.get_items_from_page(brand, i, session)

    async def get_items_from_page(self, brand: ShopItemCategoryBrand, i: int, session: aiohttp.ClientSession):
        print(brand.brand_link + f'page{i}/')
        async with session.get(brand.brand_link + f'page{i}/') as resp:
            try:
                parser = BeautifulSoup(await resp.text(), features="lxml")
            except:
                print(f"Unable to parse page {i} of brand {brand.brand_name}")
                return
        try:
            products = parser.find(name='ul', attrs={'class': 'shop-list-products row'}).find_all(name='li', attrs={
                'class': 'shop-item-product col-6 col-sm-6 col-md-4 js_shop'})
            for product in products:
                details = product.find(
                    name='div',
                    attrs={
                        'class': 'shop-item-product__name'
                    }
                ).find(name='a')
                BrandItem.get_or_create(
                    brand=brand,
                    item_link=details['href'],
                    brand_item_name=details.text
                )
        except:
            print(f"Unable to parse page {i} of brand {brand.brand_name}")
            return


async def main():
    load_dotenv()
    initialize_db()
    async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        await SmolandshopParser().parse_website(session=session)
    close_db()


if __name__ == "__main__":
    asyncio.run(main())
