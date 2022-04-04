import logging
import os.path
import re
import time
from datetime import date
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class LinksFinder:
    @staticmethod
    def find_links(url: str, path: Path):
        product_links = LinksFinder._get_product_links(url)
        LinksFinder._save_links(product_links, path)

    @staticmethod
    def _get_product_links(url: str) -> pd.DataFrame:
        product_links = []

        logging.info('Поиск ссылок на товары...')

        # Получение soup главной страницы для поиска ссылок на каталоги
        main_page_soup = BeautifulSoup(requests.get(url).text, features='html.parser')
        catalog_a_elems = main_page_soup.find_all('a', href=re.compile(r'^/catalog/.*'))
        catalog_urls = {urljoin(url, a.get('href')) for a in catalog_a_elems}

        logging.info(f'Найдено [{len(catalog_urls)}] ссылки на каталоги')

        # Поиск товаров в каталогах
        profile = webdriver.FirefoxProfile()
        profile.set_preference("permissions.default.image", 2)  # Запрет на загрузку изображений
        browser = webdriver.Firefox(firefox_profile=profile)

        for i, catalog_url in enumerate(catalog_urls, 1):
            # Получение страницы через селениум, чтобы можно было подгрузить весь контент скроллом
            browser.get(catalog_url)
            time.sleep(1)

            # Скроллинг для прогрузки всего контента в каталоге
            elem = browser.find_element(By.TAG_NAME, 'body')
            for _ in range(20):
                elem.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.2)

            header = browser.find_element(By.TAG_NAME, 'h1').text

            # Получение ссылок на странице
            product_links_current_page = []
            product_cards = browser.find_elements(By.XPATH, '//div[@class="product-card"]')
            for product_card in product_cards:
                product_name = product_card.find_element(By.CLASS_NAME, 'product-card__name').text
                product_link = product_card.find_element(By.XPATH, './a').get_attribute('href')

                if all((product_name, product_link)):
                    product_links_current_page.append({'name': product_name, 'link': product_link})

            logging.info(f'[{i}/{len(catalog_urls)}] Найдено [{len(product_links_current_page)}] ссылок на товары в каталоге [{header}]')

            # Добавление ссылок в общий лист
            product_links += product_links_current_page

        browser.quit()
        df = pd.DataFrame(product_links).drop_duplicates('name').sort_values('name')  # С удалением дубликатов и сортировкой

        logging.info(f'Поиск товаров завершен! Найдено [{len(product_links)}] уникальных ссылок')

        return df

    @staticmethod
    def _save_links(links: pd.DataFrame, path: Path):
        os.makedirs(path, exist_ok=True)
        file_path = os.path.join(path, 'links_{}.csv'.format(date.today().isoformat()))

        logging.info(f'Сохранение ссылок в [{file_path}]...')
        links.to_csv(file_path, sep=';', index=False)
        logging.info(f'Сохранение ссылок завершено!')
