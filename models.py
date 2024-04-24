import os

from dotenv import load_dotenv
from peewee import Model, CharField, ForeignKeyField, PostgresqlDatabase, SqliteDatabase, BooleanField

load_dotenv()

# db = PostgresqlDatabase(
#     database=os.environ.get('POSTGRES_DB_NAME'),
#     user=os.environ.get('POSTGRES_LOGIN'),
#     password=os.environ.get('POSTGRES_PASSWORD'),
#     host=os.environ.get('POSTGRES_HOST'),
#     port=os.environ.get('POSTGRES_PORT')
# )
#
# # db = SqliteDatabase('tabacos.db')
#
#
# class BaseModel(Model):
#     class Meta:
#         database = db
#
#
# class Shop(BaseModel):
#     shop_name = CharField(default='')
#     shop_link = CharField(default='')
#
#
# class TabacoBrand(BaseModel):
#     brand_name = CharField(default='')
#
#
# class TabacoBrandAndShop(BaseModel):
#     brand = ForeignKeyField(TabacoBrand, backref='shops')
#     shop = ForeignKeyField(Shop, backref='brands')
#
#
# class Tabaco(BaseModel):
#     tabaco_name = CharField(default='')
#     tabaco_brand = ForeignKeyField(TabacoBrand, backref='tabacos')
#     country = CharField(default='')
#     taste = CharField(default='')
#     weight = CharField(default='')
#     krepost = CharField(default='')
#     cenovoy_segment = CharField(default='')
#     dymnost = CharField(default='')
#     zharostoykost = CharField(default='')
#     stoykost_vkusa = CharField(default='')
#     sort_tabaka = CharField(default='')
#     taste_type = CharField(default='')
#     svezhest = CharField(default='')
#     sostav = CharField(default='')
#     upakovka = CharField(default='')
#     temp_hraneniya = CharField(default='')
#     srok_godnosti = CharField(default='')
#     english_name = CharField(default='')
#
#
# class TabacoLinksInShops(BaseModel):
#     tabaco = ForeignKeyField(Tabaco, backref='linksinshops')
#     shop = ForeignKeyField(Shop, backref='tabacolinks')
#     link = CharField(default='')


# def initialize_db1():
#     db.connect()
#     db.create_tables(
#         [
#             Shop,
#             TabacoBrand,
#             TabacoBrandAndShop,
#             Tabaco,
#             TabacoLinksInShops
#         ],
#         safe=True
#     )


db = SqliteDatabase('tabacos.db')


class BaseModel(Model):
    class Meta:
        database = db


class Shop(BaseModel):
    shop_name = CharField(default='')
    shop_link = CharField(default='')


class ShopItemCategory(BaseModel):
    category_name = CharField(default='')
    category_link = CharField(default='')
    shop = ForeignKeyField(Shop, backref='shopitemcategories')


class ShopItemCategoryBrand(BaseModel):
    brand_name = CharField(default='')
    brand_link = CharField(default='')
    category = ForeignKeyField(ShopItemCategory, backref='shopitemcategories')


class BrandItem(BaseModel):
    brand = ForeignKeyField(ShopItemCategoryBrand, backref='items')
    brand_item_name = CharField(default='')
    item_link = CharField(default='')
    processed = BooleanField(default=False)


def initialize_db():
    db.connect()
    db.create_tables(
        [
            Shop,
            ShopItemCategory,
            ShopItemCategoryBrand,
            BrandItem,
        ],
        safe=True
    )


def close_db():
    db.close()
