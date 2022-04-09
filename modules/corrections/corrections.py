from __future__ import annotations

__all__ = ['Correction']

from abc import ABC, abstractmethod

import pandas as pd


class Correction(ABC):
    @classmethod
    def do(cls, df: pd.DataFrame) -> pd.DataFrame:
        for c in Correction.__subclasses__():
            df = c._do(df)
        return df

    @staticmethod
    @abstractmethod
    def _do(df: pd.DataFrame) -> pd.DataFrame:
        pass


class _CorrectionFiveArm(Correction):

    @staticmethod
    def _do(df: pd.DataFrame) -> pd.DataFrame:
        words = {
            'Зеркальное литое': 'Овальное',
            'Cтальное хромированное, с прямоугольным сечением лучей': 'Прямоугольное',
            'округленным': 'прямоугольным'
        }

        # Внесение корректировок в слова
        for column in df.columns:
            for k, v in words.items():
                try:
                    df[column] = df[column].str.replace(k, v)
                except AttributeError:
                    continue

        return df


class _CorrectionDropOvalIfCan(Correction):

    @staticmethod
    def _do(df: pd.DataFrame) -> pd.DataFrame:
        words = {
            'Овальное': 'Прямоугольное',
        }

        # Внесение корректировок в слова
        for column in df.columns:
            for k, v in words.items():
                try:
                    df[column] = df[column].str.replace(k, v)
                except AttributeError:
                    continue

        df = df.drop_duplicates(subset=['Title'], keep='last')

        return df


class _CorrectionNotInSale(Correction):

    @staticmethod
    def _do(df: pd.DataFrame) -> pd.DataFrame:
        words = ['Коврик-чехол CSn', 'Коврик-чехол CSx', 'MPES']

        # Удаление товаров по ключевым словам
        df = df.drop(df[df.apply(lambda x: True if any(type(x[c]) == str and w in x[c] for w in words for c in df.columns) else False, axis=1)].index)
        return df
