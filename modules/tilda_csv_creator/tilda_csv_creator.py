import datetime
import logging
import os.path
from pathlib import Path
from typing import Iterable

import pandas as pd

from modules.corrections import Correction
from modules.reader.product import Product


class TildaCSVCreator:
    @staticmethod
    def create_csv(products: Iterable[Product], sale: float, min_price_for_sale: int, path: Path):
        logging.info('Создание CSV файла для тильды...')
        dfs = []
        for p in products:
            dfs.append(p.get_tilda_df(sale, min_price_for_sale))
        df = pd.concat(dfs, ignore_index=True)

        # Внесение корректировок в товары
        df = Correction.do(df)

        csv_file_path = os.path.join(path, f'tilda_{datetime.date.today().isoformat()}.csv')
        df.to_csv(csv_file_path, sep=';', index=False)

        logging.info(f'CSV файл создан! [{csv_file_path}]')
