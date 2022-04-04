import string
from typing import Union


class Price:
    def __init__(self, value: Union[str, float]):
        if type(value) == str:
            value = float(''.join(c for c in value if c in string.digits + '.'))
        self._value = float(value)

    def __str__(self) -> str:
        return '{:,.2f} ₽'.format(self._value)

    @property
    def value(self) -> float:
        return self._value
