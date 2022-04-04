# metta-to-tilda

Скрипт, который парсит данные товаров с [сайта metta.ru](https://metta.ru/), производителя офисных кресел Samurai, и превращает их в удобоваримый .csv файл для импорта на сайт, построенный на [конструкторе tilda](https://кресла-самурай.рф/)

# Requirements

Selenium - на сайте metta.ru используется Ajax для динамической подгрузки контента. Чтобы получить доступ к такому типу контента, селениумом производится скроллы

### Selenium

```commandline
pip install selenium 
pacman -S geckodriver
```
