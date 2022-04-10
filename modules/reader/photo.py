from __future__ import annotations

import os.path
import uuid
from typing import Optional
from urllib.parse import urljoin

import requests
from PIL import Image


class Photo:
    def __init__(self, src: str, domain: str = 'https://mks.metta.ru'):
        self._url = urljoin(domain, src)

    def __str__(self):
        return self._url

    def download(self, folder_path: str, photo_id: Optional[int] = None, photo_ext='jpg'):
        # Создаю папочку для сохранения, если она не существует
        os.makedirs(folder_path, exist_ok=True)

        # Определяюсь с именем файла. Если есть айди, то использую его, а если нет, то генерирую белеберду (редкую)
        base_name = uuid.uuid1() if photo_id is None else '{}_{}'.format(str(photo_id).zfill(2), uuid.uuid1())
        name = '{base_name}.{ext}'.format(base_name=base_name, ext=photo_ext)
        path = os.path.join(folder_path, name)

        # Сохраняю фотку через пиллоу, чтобы дополнительно с этим менялся формат. Вообще красота
        photo = Image.open(requests.get(self._url, stream=True).raw).convert('RGB')
        photo.save(path)

    @property
    def url(self) -> str:
        return self._url
