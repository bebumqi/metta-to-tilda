from __future__ import annotations

import time
from typing import Sequence, List, TypedDict

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from ..image import Image
from ..price import Price


class ProductEditionCharDict(TypedDict):
    title: str
    value: str
    image: Image


class ProductEdition:
    @staticmethod
    def _walk_through_editions(browser: webdriver.Firefox) -> List[ProductEdition]:
        body = browser.find_element(By.TAG_NAME, 'body')

        editions = []

        # Прокликивание каждой возможной модификацияя
        char_groups = browser.find_elements(By.XPATH, '//div[@class="offer-char__title"]/../div[@class="offer-char__items"]/..')

        def _walk(i=0):
            for elem in char_groups[i].find_elements(By.XPATH, './/div[@class="offer-char__item"][not(@disabled)]'):
                # Использование JS для смены модификации
                browser.execute_script("arguments[0].scrollIntoView();", elem)
                for _ in range(3):
                    body.send_keys(Keys.ESCAPE)
                    time.sleep(0.1)

                elem.click()

                if len(char_groups) > i + 1:
                    _walk(i + 1)
                else:
                    editions.append(ProductEdition._get_product_edition(browser))

        _walk()
        return editions

    @classmethod
    def _get_product_edition(cls, browser: webdriver.Firefox) -> ProductEdition:
        chars = []
        char_groups = browser.find_elements(By.XPATH, '//div[@class="offer-char__title"]/../div[@class="offer-char__items"]/..')

        for char_group in char_groups:
            # Получение заголовка характеристики
            char_title = char_group.text

            # Получение значения характеристики из выбранного изображения
            img_elem = char_group.find_element(By.XPATH, './/input[@checked]/..//img')
            char_value = img_elem.get_attribute('title')
            char_image = Image.get_from_img_elem(browser.current_url, img_elem)

            # Создание итоговой характеристики
            chars.append(ProductEditionCharDict(
                title=char_title,
                value=char_value,
                image=char_image,
            ))

        # Получение цены
        price = Price(browser.find_element(By.XPATH, '//div[@class="product__price"]').text)

        # Получение изображений модификации
        images = [Image.get_from_img_elem(browser.current_url, img)
                  for img in browser.find_elements(By.XPATH, '//div[contains(@class, "product__slider")]/img')]

        return ProductEdition(chars=chars, price=price, images=images)

    @classmethod
    def get_product_editions(cls, browser: webdriver.Firefox) -> List[ProductEdition]:
        editions = ProductEdition._walk_through_editions(browser)
        return editions

    def __init__(self, chars: List[ProductEditionCharDict], price: Price, images: List[Image]):
        self._chars = chars
        self._price = price
        self._images = images

    @property
    def name(self) -> str:
        pass

    @property
    def price(self) -> Price:
        pass

    @property
    def images(self) -> Sequence[Image]:
        pass
