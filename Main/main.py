import requests
import lxml
import sqlite3
from dataclasses import dataclass
from bs4 import BeautifulSoup
import config


@dataclass
class Product:
    sku: int
    name: str
    link: str
    price: float


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
            else:
                price = "По запросу"
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


# Печатаем все строки в БД
def print_all():
    with sqlite3.connect(config.db_name) as conn:
        cursor = conn.cursor()
    cursor.execute('SELECT * FROM source')
    answers = cursor.fetchall()
    for answer in answers:
        print(answer)


# Выбираем и сортируем по ванны по убываниюи возрастанию цены (Выводит id и цену). Для убывания 1 и для возрастания 2
def sort(parametr: int):
    if parametr == 1:
        with sqlite3.connect(config.db_name) as conn:
            cursor = conn.cursor()
        cursor.execute('SELECT id, price FROM source ORDER BY price DESC')
        results = cursor.fetchall()
        for row in results:
            print(row)
    if parametr == 2:
        with sqlite3.connect(config.db_name) as conn:
            cursor = conn.cursor()
        cursor.execute('SELECT id, price FROM source ORDER BY price ASC')
        results = cursor.fetchall()
        for row in results:
            print(row)


# Выбираем ванны у которых цена меньше определенного количества рублей (Выводит название и цену)
def the_output_is_less_than_price(max_price: int):
    with sqlite3.connect(config.db_name) as conn:
        cursor = conn.cursor()
    cursor.execute('''                                                              
    SELECT name, price
    FROM source
    GROUP BY price
    HAVING AVG(price) < ?
    ORDER BY price DESC
    ''', (max_price,))
    results = cursor.fetchall()
    for row in results:
        print(row)


if __name__ == "__main__":
    parser(url=config.url_name, max_item=521)
