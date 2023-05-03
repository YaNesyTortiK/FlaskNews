# Новостной портал

Новостной сайт на котором любой желающий может поделиться выдуманной новостью!

## Описание
Новостной сайт созданный с использованием микрофреймворка Flask в рамках обучения.

## Технологии
* Python
* Flask
* Sqlite3

## Как запустить

1. Склонируйте репозиторий
2. Создайте и активируйте виртаульное окружение
```commandline
python -m venv venv
source venv/Scripts/activate
```  
3. Установите зависимости
```commandline
pip install -r requirements.txt
```
4. Создайте файл .env и укажите SECRET_KEY.
```commandline
SECRET_KEY=YOUR_SECRET_KEY
```
5. Измените путь к базе данных в файле init.py на используемый. База данных должна быть sqlite! (Таблицы будут созданы автоматически)

6. Измените логин (email) администратора в файле static\data\users\admins.json
- Пример для учетной записи одного администратора:
```commandline
[
    "admin@email.com"
]
```
- Пример для нескольких учетных записей:
```commandline
[
    "admin1@email.com",
    ...
    "admin...@email.com"
]
```

7. Запустите flask приложение
```commandline
flask run
```
