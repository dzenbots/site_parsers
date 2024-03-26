from peewee import SqliteDatabase, Model, CharField, ForeignKeyField

db = SqliteDatabase("tabaco_shops.sqlite", pragmas={'foreign_keys': 1})


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
    ...


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
