from __future__ import annotations

import hashlib
import json
import logging
import re
from typing import List, Sequence

import bs4
import pandas as pd

from categories import CATEGORIES
from .product_edition import ProductEdition
from ..photo import Photo
from ..price import Price


class Product:
    @classmethod
    def get_from_page(cls, soup: bs4.BeautifulSoup) -> Product:
        # Получение json продукта. В большинстве интернет-магазинов на Bitrix на странице есть информация такого формата.
        # Включает в себя все модификации товара, цены и ссылки на фотографии
        data = re.findall(r"new ProductCard\((.*?)\);", str(soup))[0]
        product_json = json.loads(data, strict=False)

        # Получение основных данных о продукте
        price = Price(soup.find('div', {'class': 'product__price'}).text)
        product = cls(
            name=soup.find('title').text,
            price=price,
            photos=[Photo(p['SRC']) for p in product_json['product']['photos']]
        )

        product.description = str(soup.find('div', {'data-tab': 'descr'}))
        product.characteristics = str(soup.find('div', {'data-tab': 'char'}))

        # Создание вариантов продукта
        product.editions = ProductEdition.get_product_editions(product_json)
        return product

    def __init__(self, name: str, price: Price, photos: Sequence[Photo]):
        self._name = name
        self._price = price
        self._photos = list(photos)
        self._categories = self._get_categories_by_name(self._name)

        self._editions = []

        self._description = ''
        self._characteristics = ''

    def __str__(self) -> str:
        return self._name

    @staticmethod
    def _get_categories_by_name(name: str) -> List[str]:
        categories = []
        for category_name, category_regex in CATEGORIES.items():
            if category_regex.search(name):
                categories.append(category_name)
        return categories

    @property
    def name(self) -> str:
        return self._name

    @property
    def price(self) -> Price:
        return self._price

    @property
    def photos(self) -> List[Photo]:
        return self._photos

    @property
    def categories(self) -> List[str]:
        return self._categories

    @property
    def editions(self) -> List[ProductEdition]:
        return self._editions

    @editions.setter
    def editions(self, value: Sequence[ProductEdition]):
        self._editions = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

        if not value:
            logging.warning(f'У продукта [{self._name}] не найдено описание')

    @property
    def characteristics(self):
        return self._characteristics

    @characteristics.setter
    def characteristics(self, value: str):
        self._characteristics = value

        if not value:
            logging.warning(f'У продукта [{self._name}] не найдены характеристики')

    def get_tilda_df(self, sale=.0, min_price_for_sale=.0) -> pd.DataFrame:
        def hash_string(string) -> str:
            return hashlib.md5(string.encode('utf-8')).hexdigest()

        # Получение ID главного товара для привязки к нему других товаров
        parent_id = hash_string(self._name)

        # Добавление скидки, если есть и если подходит по минимальной цене
        for edition in self.editions:
            if edition.price.value > min_price_for_sale:
                edition.price.sale = sale

        # Создание главной строки товара
        rows = [{
            'Category': ';'.join(self.categories),
            'Title': self.name,
            'Text': self.description,
            'Mark': '' if not self.editions else self.editions[0].price.sale_mark,
            'Photo': self.photos[0].url,
            'External ID': parent_id
        }]

        # Создание модификаций товара
        for edition in self.editions:
            rows.append({
                'Title': edition.name,
                'Price': edition.price.value_with_sale,
                'Price Old': edition.price.value,
                'Parent External ID': parent_id,
                'External ID': hash_string(edition.name),
                'Editions': edition.properties_str,
                'Photo': ' '.join(p.url for p in edition.photos)
            })

        tilda_df = pd.DataFrame(
            data=rows,
            columns=['Brand', 'Mark', 'Category', 'Title', 'Description', 'Text', 'Photo', 'Price',
                     'Price Old', 'Editions', 'Modifications', 'External ID', 'Parent External ID']
        )

        return tilda_df
