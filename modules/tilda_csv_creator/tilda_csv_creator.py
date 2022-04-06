import datetime
import logging
import os.path
from pathlib import Path
from typing import Iterable

import pandas as pd

from corrections import CORRECTIONS_WORDS, CORRECTIONS_SOLED
from modules.reader.product import Product


class TildaCSVCreator:
    @staticmethod
    def create_csv(products: Iterable[Product], sale: float, min_price_for_sale: int, path: Path):
        logging.info('Создание CSV файла для тильды...')
        dfs = []
        for p in products:
            dfs.append(p.get_tilda_df(sale, min_price_for_sale))
        df = pd.concat(dfs, ignore_index=True)

        # Внесение корректировок в слова
        for column in df.columns:
            for k, v in CORRECTIONS_WORDS.items():
                try:
                    df[column] = df[column].str.replace(k, v)
                except AttributeError:
                    continue

        # Изменения количества товара на ноль по ключевым словам
        df['Quantity'] = df.apply(
            lambda x: 0 if any(type(x[c]) == str and w in x[c] for w in CORRECTIONS_SOLED for c in df.columns) else None,
            axis=1
        )

        csv_file_path = os.path.join(path, f'tilda_{datetime.date.today().isoformat()}.csv')
        df.to_csv(csv_file_path, sep=';', index=False)

        logging.info(f'CSV файл создан! [{csv_file_path}]')
