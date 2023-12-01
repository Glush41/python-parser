import requests
import lxml
import sqlite3
from dataclasses import dataclass
from bs4 import BeautifulSoup

@dataclass
class Product:
    sku: int
    name: str
    link: str
    price: float

def Create_DB():
    connection = sqlite3.connect('glavsnab.db')
    connection.execute("""
        CREATE TABLE IF NOT EXISTS source (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            sku INTEGER,
            name TEXT NOT NULL,
            link TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)
    print("Database has been created")


def parser(url:str, max_item: int):
    page = 1
    count_items = 0
    Create_DB()
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
            sku = product.find("span", class_ = "product-card__key").text
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
        Insert_db(list_product)
        page += 1



def Insert_db (products: list[Product]):
    connection = sqlite3.connect('glavsnab.db')
    cursor = connection.cursor()
    for product in products:
        cursor.execute('INSERT INTO source (sku, name, link, price) VALUES (?, ?, ?, ?)', (product.sku, product.name, product.link, product.price))
    connection.commit()
    connection.close()

#Печатаем все строки в БД
def Print_all():
    connection = sqlite3.connect('glavsnab.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM source')
    answers = cursor.fetchall()
    for answer in answers:
      print(answer)
    connection.close()

# Выбираем и сортируем по ванны по убыванию цены (Выводит id и цену)
def Sort_in_descending_order():
    connection = sqlite3.connect('glavsnab.db')
    cursor = connection.cursor()
    cursor.execute('SELECT id, price FROM source ORDER BY price DESC')
    results = cursor.fetchall()
    for row in results:
      print(row)
    connection.close()

# Выбираем и сортируем по ванны по возрастанию цены (Выводит id и цену)
def Sort_in_ascending_order():
    connection = sqlite3.connect('glavsnab.db')
    cursor = connection.cursor()
    cursor.execute('SELECT id, price FROM source ORDER BY price ASC')
    results = cursor.fetchall()
    for row in results:
      print(row)
    connection.close()

# Выбираем ванны у которых цена больше 50000 рублей (Выводит название и цену)
def The_output_is_more_than_price():
    connection = sqlite3.connect('glavsnab.db')
    cursor = connection.cursor()
    cursor.execute('''                                                              
    SELECT name, price
    FROM source
    GROUP BY price
    HAVING AVG(price) > ?
    ORDER BY price DESC
    ''', (50000,))
    results = cursor.fetchall()
    for row in results:
      print(row)
    connection.close()

if __name__ == "__main__":
    parser(url="https://glavsnab.net/santehnika/vanny-2/akrilovye-vanny.html?limit=100", max_item=521)