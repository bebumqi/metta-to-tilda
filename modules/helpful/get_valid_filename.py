import string as s

VALID_CHARS = f'{s.ascii_letters}{s.digits}абвгдежзийклмнопрстуфхцчшщъыьэюяАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ-_.() '


def get_valid_filename(text: str):
    filename = ''.join(c for c in text if c in VALID_CHARS).replace(' ', '_')
    return filename
