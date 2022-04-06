from __future__ import annotations

from typing import Sequence, List, Dict

from ..photo import Photo
from ..price import Price


class ProductEditionPropertiesDict(Dict):
    name: str
    value: str


class ProductEdition:
    @classmethod
    def get_product_editions(cls, product_json: dict) -> List[ProductEdition]:
        editions = []

        for offer in product_json['offers']:  # Оффер содержит в себе всё необходимое
            editions.append(
                ProductEdition(
                    product_name=product_json['product']['name'],
                    properties=[ProductEditionPropertiesDict(**p) for p in offer['properties']],
                    price=Price(offer['price']['value']),
                    photos=[Photo(p['SRC']) for p in offer['photos']]
                )
            )

        return editions

    def __init__(self, product_name: str, properties: List[ProductEditionPropertiesDict], price: Price, photos: List[Photo]):
        self._properties = properties
        self._price = price
        self._photos = photos
        self._name = '{} / {}'.format(product_name, " ".join([v['value'] for v in self._properties]))

    @property
    def name(self) -> str:
        return self._name

    @property
    def price(self) -> Price:
        return self._price

    @property
    def photos(self) -> Sequence[Photo]:
        return self._photos

    @property
    def properties_str(self) -> str:
        return ';'.join([f'{p["name"]}:{p["value"]}' for p in self._properties])
