import string
from typing import Union


class Price:
    def __init__(self, value: Union[str, float]):
        if type(value) == str:
            value = float(''.join(c for c in value if c in string.digits + '.'))
        self._value = float(value)
        self._sale = 0

    def __str__(self) -> str:
        return '{:,.2f} ₽'.format(self._value)

    @property
    def value(self) -> float:
        return self._value

    @property
    def value_with_sale(self) -> float:
        if self.sale_is_percent:
            return self._value * (1 - self._sale)
        else:
            return self._value - self._sale

    @property
    def sale(self) -> float:
        return self._sale

    @sale.setter
    def sale(self, value: float):
        assert value >= 0
        self._sale = value

    @property
    def sale_mark(self) -> str:
        if self._sale:
            if self.sale_is_percent:
                return 'Скидка {}%'.format(round(self._sale * 100))
            else:
                return 'Скидка {} ₽'.format(round(self._sale))
        else:
            return ''

    @property
    def sale_is_percent(self) -> bool:
        return self._sale < 1
