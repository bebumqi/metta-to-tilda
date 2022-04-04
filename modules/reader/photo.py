from __future__ import annotations

from urllib.parse import urljoin


class Photo:
    def __init__(self, src: str, domain: str = 'https://mks.metta.ru'):
        self._url = urljoin(domain, src)

    def __str__(self):
        return self._url

    def download(self, path: str):
        pass

    @property
    def url(self) -> str:
        return self._url
