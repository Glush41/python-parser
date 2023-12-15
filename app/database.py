import sqlite3
import config
import requests
import lxml
from dataclasses import dataclass
from bs4 import BeautifulSoup


def create_DB():
    with sqlite3.connect(config.db_name) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS source (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            sku INTEGER,
            name TEXT NOT NULL,
            link TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)
    print("Database has been created")


@dataclass
class Product:
    sku: int
    name: str
    link: str
    price: float


def parser(url: str, max_item: int):
    page = 1
    count_items = 0
    create_DB()
    while max_item > count_items:
        list_product = []
        res = requests.get(f"{url}&p={page}")
        soup = BeautifulSoup(res.text, "lxml")
        products = soup.find_all("div", class_="product-card")

        for product in products:
            if count_items >= max_item:
                break
            count_items += 1
            name = product.get("data-product-name")
            sku = product.find("span", class_="product-card__key").text
            name_elem = product.find("meta", itemprop="name")
            link = name_elem.findNext().get("href")
            price_elem = product.find("span", itemprop="price")
            if price_elem:
                price = price_elem.get("content")
            list_product.append(Product(sku=sku,
                                        name=name,
                                        link=link,
                                        price=price))
        insert_db(list_product)
        page += 1


def insert_db(products: list[Product]):
    with sqlite3.connect(config.db_name) as conn:
        cursor = conn.cursor()
    for product in products:
        cursor.execute('INSERT INTO source (sku, name, link, price) VALUES (?, ?, ?, ?)',
                       (product.sku, product.name, product.link, product.price))
    conn.commit()


def sort_desc():
    with sqlite3.connect(config.db_name) as conn:
        cursor = conn.cursor()
    answers = cursor.execute('SELECT id, price, link FROM source ORDER BY price DESC').fetchall()
    print(answers)
    return answers


def sort_asc():
    with sqlite3.connect(config.db_name) as conn:
        cursor = conn.cursor()
    answers = cursor.execute('SELECT id, price, link FROM source ORDER BY price ASC').fetchall()
    return answers


if __name__ == "__main__":
    parser(url=config.url_name, max_item=524)
