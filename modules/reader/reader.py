import logging
from pathlib import Path
from queue import Queue, Empty
from threading import Thread
from typing import List

import pandas as pd
from selenium import webdriver
from tqdm import tqdm

from ..helpful import get_latest_file_in_folder
from ..reader.product import Product


class Reader:
    @staticmethod
    def get_products(links_path: Path, processes: int) -> List[Product]:
        logging.info('Считываю страницы...')
        products = []

        try:
            links_file_path = get_latest_file_in_folder(links_path, 'links*.csv')
            df_links = pd.read_csv(filepath_or_buffer=links_file_path, sep=';')
        except ValueError:
            logging.error('Ошибка при получении файла со ссылками! [{}]'.format(links_path))
            return products

        logging.info(f'Список из [{len(df_links)}] ссылок на товары получен!')

        # Создание очередей для получения результатов
        q_links = Queue(maxsize=1)
        q_products = Queue()

        # Создание потоков для обработки ссылок
        logging.info(f'Создание [{processes}] потоков для обработки ссылок...')
        threads = []
        for i in range(processes):
            threads.append(Thread(target=Reader._get_product_from_links_queue, args=(q_links, q_products)))
            threads[i].start()

        # Добавление ссылок в очередь
        for row in tqdm(df_links.itertuples(index=False), desc='Считывание страниц', total=len(df_links)):
            q_links.put(row)

        for thread in threads:
            thread.join()

    @staticmethod
    def _get_product_from_links_queue(q_links: Queue, q_products: Queue):
        """
        Функция для потока преобразования ссылки в продукт
        :param q_links:
        :param q_products:
        :return:
        """

        profile = webdriver.FirefoxProfile()
        # profile.set_preference("permissions.default.image", 2)  # Запрет на загрузку изображений
        browser = webdriver.Firefox(firefox_profile=profile)

        while q_links.qsize():
            try:
                product_name, product_link = tuple(q_links.get(timeout=10))
            except Empty:
                break

            browser.get(product_link)
            product = Product.get_from_page(browser)

        browser.quit()
