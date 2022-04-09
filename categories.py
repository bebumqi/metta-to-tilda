"""
Файл содержит паттерны regex для определения товаров в категории по названию, т.к. на metta.ru нет четкого разделения
"""
import re

CATEGORIES = {
    'Samurai S': re.compile(r'Samurai S\b'),
    'Samurai SL': re.compile(r'Samurai SL\b'),
    'Samurai K': re.compile(r'Samurai K\b'),
    'Samurai KL': re.compile(r'Samurai KL\b'),
    'Samurai Black Edition': re.compile(r'Black Edition'),
    'Samurai Lux': re.compile(r'Lux'),
    'Samurai T': re.compile(r'Samurai TV?\b'),
    'Samurai Comfort': re.compile(r'Comfort'),
    'Samurai (Модульные)': re.compile(r'Комплект\b'),
    'Samurai (Другие)': re.compile(r'(Black Edition)|(Lux\b)|(TV?\b)|(Comfort\b)'),
    'Metta L': re.compile(r'Metta L\b'),
    'Metta B': re.compile(r'Metta B\b'),
    'Аксессуары': re.compile(r'Коврик-чехол'),
    'Комплектующие': re.compile(r'(Механизм)|(Основание)|(Пятилучье)|(Синхромеханизм)|(Газ-лифт)'),
    'MPES': re.compile(r'MPES\b')
}
