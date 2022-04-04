import logging
import os
from multiprocessing import Process, Queue
from pathlib import Path
from queue import Empty
from typing import List

from bs4 import BeautifulSoup

from ..reader.product import Product


class Reader:
    @staticmethod
    def get_products(tmp_path: Path, processes: int) -> List[Product]:
        products = []
        logging.info('Считываю сохраненные страницы...')

        scrap_path = os.path.join(tmp_path, 'scrap')
        scrap_files = [os.path.join(scrap_path, f) for f in os.listdir(scrap_path) if '.html' in f]

        logging.info(f'Найдено [{len(scrap_files)}] сохраненная страница!')

        # Создание очередей для получения результатов
        q_scrap_file_paths = Queue(maxsize=1)
        q_products = Queue()

        # Создание потоков для обработки ссылок
        logging.info(f'Создание [{processes}] потоков для обработки сохраненных страниц...')
        threads = []
        for i in range(processes):
            threads.append(Process(target=Reader._get_product_from_saved_page, args=(q_scrap_file_paths, q_products)))
            threads[i].start()

        for i, file_path in enumerate(scrap_files, 1):
            logging.info(f'[{i}/{len(scrap_files)}] Считывание [{file_path}]')
            q_scrap_file_paths.put(file_path)

        # Получаю результаты считываний
        while len(products) < len(scrap_files):
            products.append(q_products.get())

        logging.info('Считывание файлов завершено!')
        return products

    @staticmethod
    def _get_product_from_saved_page(q_scrap_file_paths: Queue, q_products: Queue):
        """
        Функция для потока преобразования страницы в продукт
        :param q_scrap_file_paths:
        :param q_products:
        :return:
        """

        while True:
            try:
                file_path = q_scrap_file_paths.get(timeout=5)
            except Empty:
                break

            with open(file_path, mode='r', encoding='utf-8') as file:
                soup = BeautifulSoup(file.read(), features='html.parser')
            q_products.put(Product.get_from_page(soup))
