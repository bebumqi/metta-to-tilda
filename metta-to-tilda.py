import argparse
import logging
import os
import pathlib

from modules import Reader, TildaCSVCreator, ImagesDownloader, LinksFinder

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

parser = argparse.ArgumentParser(description='Скрипт, который парсит данные товаров с сайта metta.ru, производителя '
                                             'офисных кресел Samurai, и превращает их в удобоваримый .csv файл '
                                             'для импорта на сайт, построенный на конструкторе tilda')

parser.add_argument('-l', '--links', action='store_true', help='Ищет ссылки на страницы товаров для последующей обработки')
parser.add_argument('-c', '--csv', action='store_true', help='Обрабатывает страницы в .csv для tilda')
parser.add_argument('-i', '--download_images', action='store_true', help='Скачивает изображения товаров')

parser.add_argument('--url', default='https://msk.metta.ru/', type=str, help='Ссылка на сайт-донар')
parser.add_argument('--tmp', default='tmp', type=pathlib.Path, help='Путь к временному хранилищу данных')
parser.add_argument('--output', default='output', type=pathlib.Path, help='Путь для сохранения .csv файлов')
parser.add_argument('--sale', default=0, type=float, help='Скидка на товары, относительно цены производителя. '
                                                          'Если 0 < sale < 1, то воспринимается, как процент, иначе как рубли')
parser.add_argument('--min_price_for_sale', default='16900', type=int, help='Минимальная цена для применения скидки')
parser.add_argument('-p', '--processes', default=os.cpu_count(), type=int, help='Количество процессов при обработке исходников. По умолчанию равняется количеству ядер ЦП')

args = parser.parse_args()

if __name__ == '__main__':
    # Создание папок для файлов, если они не существуют
    os.makedirs(args.tmp, exist_ok=True)
    os.makedirs(args.output, exist_ok=True)

    # Создание исходников файлов, если необходимо
    if args.links:
        LinksFinder.find_links(url=args.url, path=args.tmp)

    # Создание .csv файла, если необходимо
    if args.csv or args.download_images:
        # Считывание исходников
        products = Reader.get_products(links_path=args.tmp, processes=args.processes)

        # Скачивание изображений товаров
        if args.download_images:
            ImagesDownloader.download(products=products, path=args.output)

        # Сохранение .csv файла
        if args.csv:
            TildaCSVCreator.create_csv(products=products, sale=args.sale, min_price_for_sale=args.min_price_for_sale, path=args.output)
