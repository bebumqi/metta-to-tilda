from __future__ import annotations

import logging

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

from .product_edition import ProductEdition
from ..price import Price


class Product:
    @classmethod
    def get_from_page(cls, browser: webdriver.Firefox) -> Product:
        # Получение основных данных о продукте
        price = Price(browser.find_element(By.XPATH, '//div[@class="product__price"]').text)
        product = cls(
            name=browser.title,
            link=browser.current_url,
            price=price
        )

        product.description = browser.find_element(By.XPATH, '//div[@data-tab="descr"]').get_attribute('innerHTML')
        product.characteristics = browser.find_element(By.XPATH, '//div[@data-tab="char"]').get_attribute('innerHTML')

        # Создание вариантов продукта
        editions = ProductEdition.get_product_editions(browser)

        return product

    def __init__(self, name: str, link: str, price: Price):
        self._name = name
        self._link = link
        self._price = price
        self._editions = []

        self._description = ''
        self._characteristics = ''

    @property
    def price(self) -> Price:
        return self._price

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

        if not value:
            logging.warning(f'У продукта [{self._name}] не найдено описание [{self._link}]')

    @property
    def characteristics(self):
        return self._characteristics

    @characteristics.setter
    def characteristics(self, value: str):
        self._characteristics = value

        if not value:
            logging.warning(f'У продукта [{self._name}] не найдены характеристики [{self._link}]')

    def get_df_tilda(self) -> pd.DataFrame:
        pass
