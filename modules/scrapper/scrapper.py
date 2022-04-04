import logging
import os.path
import re
import shutil
import time
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from modules.helpful import get_valid_filename


class Scrapper:
    @staticmethod
    def scrap(url: str, path: Path):
        product_links = Scrapper._get_product_links(url)
        Scrapper._save_pages(product_links, path)

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
            body_elem = browser.find_element(By.TAG_NAME, 'body')
            for _ in range(20):
                for k in (Keys.PAGE_DOWN, Keys.ESCAPE):  # ESCAPE Необходимо, чтобы закрывать pupup'ы
                    body_elem.send_keys(k)
                    time.sleep(0.1)

            header = browser.find_element(By.TAG_NAME, 'h1').text
            product_cards = browser.find_elements(By.XPATH, '//div[@class="product-card"]')
            product_links_current_page = []

            for product_card in product_cards:
                product_name = product_card.find_element(By.CLASS_NAME, 'product-card__name').text
                product_link = product_card.find_element(By.XPATH, './a').get_attribute('href')

                if all((product_name, product_link)):
                    product_links_current_page.append({'name': product_name, 'link': product_link})

            logging.info(f'[{i}/{len(catalog_urls)}] Найдено [{len(product_links_current_page)}] ссылок на товары в каталоге [{header}]')

            # Добавление ссылок в общий лист
            product_links += product_links_current_page

        browser.quit()
        logging.info(f'Поиск товаров завершен! Найдено [{len(product_links)}] уникальных ссылок')

        df = pd.DataFrame(product_links).drop_duplicates('name').sort_values('name')  # С удалением дубликатов и сортировкой
        return df

    @staticmethod
    def _save_pages(links: pd.DataFrame, path: Path):
        path = os.path.join(path, 'scrap')
        if os.path.isdir(path):
            logging.info(f'Каталог сохранения не пуст. Очистка содержимого в [{path}]...')
            shutil.rmtree(path, ignore_errors=False, onerror=None)
        os.makedirs(path, exist_ok=True)

        logging.info(f'Сохранение страниц в [{path}]...')

        for i, (name, link) in enumerate(links.itertuples(index=False), 1):
            html = requests.get(link).text
            soup = BeautifulSoup(html, features='html.parser')
            header = soup.find('h1').text
            path_full = os.path.join(path, '{}.html'.format(get_valid_filename(header)))
            with open(path_full, mode='w', encoding='utf-8') as file:
                file.write(html)

            logging.info(f'[{i}/{len(links)}] Сохранен [{path_full}]')

        logging.info(f'Сохранение страниц завершено!')
