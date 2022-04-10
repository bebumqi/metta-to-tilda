import logging
import os
import shutil
import time
from pathlib import Path
from queue import Queue, Empty
from threading import Thread
from typing import List

from ..helpful import get_valid_filename
from ..reader.product import Product


class PhotosDownloader:
    @staticmethod
    def download(products: List[Product], path: Path, threads_count=32, sleep_sec=0.5):
        logging.info('Начинаю загрузку изображений товаров...')

        path = os.path.join(path, 'photos')
        if os.path.isdir(path):
            logging.info(f'Каталог сохранения не пуст. Очистка содержимого в [{path}]...')
            shutil.rmtree(path, ignore_errors=False, onerror=None)
        os.makedirs(path, exist_ok=True)

        # Создание очередей для получения результатов
        q_products = Queue(maxsize=1)

        # Создание потоков для сохранения товаров
        logging.info(f'Создание [{threads_count}] потоков для сохранения товаров...')
        threads = []
        for i in range(threads_count):
            threads.append(Thread(target=PhotosDownloader._download_photo_thread, args=(path, q_products, sleep_sec)))
            threads[i].start()

        for i, product in enumerate(products, 1):
            logging.info(f'[{i}/{len(products)}] Сохранение [{product.name}]...')
            q_products.put((i, product))
            time.sleep(sleep_sec)  # Отдых, чтобы не получить бан

        logging.info('Сохранение фотографий завершено!')

    @staticmethod
    def _download_photo_thread(path: str, q_products: Queue, sleep_sec):
        while True:
            try:
                i, product = q_products.get(timeout=30)
            except Empty:
                break

            product_path = os.path.join(path, get_valid_filename(product.name))

            # Сохранение основных фотографий товара
            for photo_id, photo in enumerate(product.photos, 1):
                # Скачивание фотки
                photo.download(product_path, photo_id=photo_id, photo_ext='jpg')
                time.sleep(sleep_sec)  # Отдых, чтобы не получить бан

            # Сохранение модификаций товаров
            for edition_id, edition in enumerate(product.editions, 1):
                edition_path = os.path.join(
                    product_path,
                    get_valid_filename('{}_{}'.format(str(edition_id).zfill(2), edition.name))
                )

                for edition_photo_id, edition_photo in enumerate(edition.photos, 1):
                    # Скачивание фотки
                    edition_photo.download(edition_path, photo_id=edition_photo_id, photo_ext='jpg')
                    time.sleep(sleep_sec)  # Отдых, чтобы не получить бан
