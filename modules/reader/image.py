from __future__ import annotations

from urllib.parse import urljoin

from selenium.webdriver.remote.webelement import WebElement


class Image:
    @classmethod
    def get_from_img_elem(cls, current_url: str, img_elem: WebElement) -> Image:
        return Image(urljoin(current_url, img_elem.get_attribute('src')).split('?')[0])

    def __init__(self, src: str):
        self._src = src

    def __str__(self):
        return self._src

    def download(self, path: str):
        pass
