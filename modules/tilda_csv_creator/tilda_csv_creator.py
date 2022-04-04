from pathlib import Path
from typing import Iterable

from modules.reader.product import Product


class TildaCSVCreator:
    @staticmethod
    def create_csv(products: Iterable[Product], sale: float, min_price_for_sale: int, path=Path):
        pass
