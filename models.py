import os

from peewee import SqliteDatabase, Model, CharField, ForeignKeyField, MySQLDatabase

db = SqliteDatabase("tabaco_shops.sqlite", pragmas={'foreign_keys': 1})

# db = MySQLDatabase(
#     host=os.environ.get('MYSQL_URL'),
#     user=os.environ.get('MYSQL_USER'),
#     password=os.environ.get('MYSQL_PASSWORD'),
#     database=os.environ.get('MYSQL_DB_NAME'),
#     port=os.environ.get('MYSQL_PORT'),
# )


class BaseModel(Model):
    class Meta:
        database = db


class Shop(BaseModel):
    shop_name = CharField(default='')
    shop_link = CharField(default='')


class TabacoBrand(BaseModel):
    brand_name = CharField(default='')


class TabacoBrandAndShop(BaseModel):
    brand = ForeignKeyField(TabacoBrand, backref='shops')
    shop = ForeignKeyField(Shop, backref='brands')


class Tabaco(BaseModel):
    tabaco_name = CharField(default='')
    tabaco_brand = ForeignKeyField(TabacoBrand, backref='tabacos')
    country = CharField(default='')
    taste = CharField(default='')
    weight = CharField(default='')
    krepost = CharField(default='')
    cenovoy_segment = CharField(default='')
    dymnost = CharField(default='')
    zharostoykost = CharField(default='')
    stoykost_vkusa = CharField(default='')
    sort_tabaka = CharField(default='')
    taste_type = CharField(default='')
    svezhest = CharField(default='')
    sostav = CharField(default='')
    upakovka = CharField(default='')
    temp_hraneniya = CharField(default='')
    srok_godnosti = CharField(default='')
    english_name = CharField(default='')


class TabacoLinksInShops(BaseModel):
    tabaco = ForeignKeyField(Tabaco, backref='linksinshops')
    shop = ForeignKeyField(Shop, backref='tabacolinks')
    link = CharField(default='')


def initialize_db():
    db.connect()
    db.create_tables(
        [
            Shop,
            TabacoBrand,
            TabacoBrandAndShop,
            Tabaco,
            TabacoLinksInShops
        ],
        safe=True
    )
