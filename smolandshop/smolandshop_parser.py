import asyncio

import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from models import initialize_db, close_db, Shop, Type, Brand, Product, Characteristic, Svod

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
            print(f"Unable to connect to {base_url}")
            return
        try:
            types = parser.find(
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
        for type_item in types:
            try:
                Type.get_or_create(
                    type_name=type_item.find('a').text,
                    type_link=type_item.find('a')['href']
                )
            except:
                print(f"Unable to parse category")
        await self.process_types(session=session, shop=shop)

    async def process_types(self, session: aiohttp.ClientSession, shop: Shop):
        for type_item in Type.select():
            async with session.get(type_item.type_link) as resp:
                try:
                    parser = BeautifulSoup(await resp.text(), features="lxml")
                except:
                    print(f"Unable to get brands from {type_item.type_link}")
                    return
            try:
                brands = parser.find(name='div', attrs={'class': 'shop-block-categories'}).find_all(
                    name='div',
                    attrs={
                        'class': 'h2'
                    }
                )
            except:
                print(f"Unable to get brands from {type_item.type_link}")
                return
            for brand in brands:
                brand_item, created = Brand.get_or_create(
                    brand_name=brand.find(name='a').text,
                    brand_link=brand.find(name='a')['href']
                )
                await self.process_brand(type_item=type_item, brand=brand_item, session=session, shop=shop)
        await self.parse_products(session=session)

    async def process_brand(self, type_item: Type, brand: Brand, session: aiohttp.ClientSession, shop: Shop):
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
            await self.get_items_from_page(brand, i, type_item, session)
        await self.parse_products(session=session, brand=brand, shop=shop)

    async def get_items_from_page(self, brand: Brand, i: int, type_item: Type, session: aiohttp.ClientSession):
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
                Product.get_or_create(
                    type=type_item,
                    brand=brand,
                    product_link=details['href'],
                    product_name=''.join(
                        item for item in ' '.join(details.text[:details.text.rfind('г')].strip().split(' ')[:-1]))
                )
        except:
            print(f"Unable to parse page {i} of brand {brand.brand_name}")
            return

    async def parse_products(self, session: aiohttp.ClientSession, brand: Brand, shop: Shop):
        for product in brand.products:
            async with session.get(product.product_link) as resp:
                try:
                    parser = BeautifulSoup(await resp.text(), features="lxml")
                except:
                    print(f"Unable to parse product {product.type.type_name} {product.brand.brand_name} {product.product_name}")
                    return
            try:
                Product.update(
                    picture_link=parser.find(name='div', attrs={'class': 'shop-product js_shop'}).find(name='img')['src']
                ).where(Product.id == product.id).execute()
                product_info = parser.find(name='div', attrs={'class': 'shop-product__details col-12 col-md-6 col-lg-8 col-xl-6'})
                characteristics = product_info.find(name='ul', attrs={'class': 'shop-product__properties'}).find_all(name='li', attrs={'class': 'shop-product__property'})
                for characteristic in characteristics:
                    characteristic_item, created = Characteristic.get_or_create(
                        characteristic_name=characteristic.text.split(':')[0].strip()
                    )
                    Svod.get_or_create(
                        product=product,
                        characteristic=characteristic_item,
                        shop=shop,
                        value=''.join(characteristic.text.split(':')[1:]).strip()
                    )
                Product.update(
                    processed=True
                ).where(Product.id == product.id).execute()
            except:
                print(f"Unable to parse product {product.type.type_name} {product.brand.brand_name} {product.product_name}")
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
