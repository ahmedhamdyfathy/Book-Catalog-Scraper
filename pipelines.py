# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import sqlite3
import os

class BookscraperPipeline:

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        ## Strip all whitespaces from strings
        field_names = adapter.field_names()
        for field_name in field_names:
            if field_name != 'description':
                value = adapter.get(field_name)
                adapter[field_name] = value.strip()

        ## Category & Product Type --> switch to lowercase
        lowercase_keys = ['category', 'product_type']
        for lowercase_key in lowercase_keys:
            value = adapter.get(lowercase_key)
            adapter[lowercase_key] = value.lower()

        ## Price --> convert to float
        price_keys = ['price', 'price_excl_tax', 'price_incl_tax', 'tax']
        for price_key in price_keys:
            value = adapter.get(price_key)
            value = value.replace('£', '')
            adapter[price_key] = float(value)

        ## Availability --> extract number of books in stock
        availability_string = adapter.get('availability')
        split_string_array = availability_string.split('(')
        if len(split_string_array) < 2:
            adapter['availability'] = 0
        else:
            availability_array = split_string_array[1].split(' ')
            adapter['availability'] = int(availability_array[0])

        ## Reviews --> convert string to number
        num_reviews_string = adapter.get('num_reviews')
        adapter['num_reviews'] = int(num_reviews_string)

        ## Stars --> convert text to number
        stars_string = adapter.get('stars')
        split_stars_array = stars_string.split(' ')
        stars_text_value = split_stars_array[1].lower()
        if stars_text_value == "zero":
            adapter['stars'] = 0
        elif stars_text_value == "one":
            adapter['stars'] = 1
        elif stars_text_value == "two":
            adapter['stars'] = 2
        elif stars_text_value == "three":
            adapter['stars'] = 3
        elif stars_text_value == "four":
            adapter['stars'] = 4
        elif stars_text_value == "five":
            adapter['stars'] = 5
        return item


class SqliteDemoPipeline:

    def __init__(self):
        ## Create/Connect to database
        folder_path = r'##local path'
        db_path = os.path.join(folder_path, 'demo.db')
        self.con = sqlite3.connect(db_path)
        ## Create cursor, used to execute commands
        self.cur = self.con.cursor()

        ## Create book table if none exists

        self.cur.execute("""
         CREATE TABLE IF NOT EXISTS books(
            id INTEGER PRIMARY KEY,
            url VARCHAR(225),
            title text,
            upc VARCHAR(225),
            product_type VARCHAR(225),
            price_excl_tax DECIMAL,
            price_incl_tax DECIMAL,
            tax DECIMAL,
            availability INTEGER,
            num_reviews INTEGER,
            stars INTEGER,
            category VARCHAR(225),
            description text,
            price DECIMAL)
            
        """)

    def process_item(self, item, spider):
        ## Define insert statement
        self.cur.execute("""
            INSERT INTO books (
            url, 
            title, 
            upc, 
            product_type,
            price_excl_tax,
            price_incl_tax,
            tax,
            availability,
            num_reviews,
            stars,
            category,
            description,
            price
              ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
                         (
                             item["url"],
                             item["title"],
                             item["upc"],
                             item["product_type"],
                             item["price_excl_tax"],
                             item["price_incl_tax"],
                             item["tax"],
                             item["availability"],
                             item["num_reviews"],
                             item["stars"],
                             item["category"],
                             item["description"],
                             item["price"],

                         ))

        ## Execute insert of data into database
        self.con.commit()
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.con.close()
