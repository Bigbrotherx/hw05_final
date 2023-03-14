# Yatube

![1678782767256](image/README/1678782767256.png)

### **Проект выполнен в рамках обучения в YandexPracticum.**

Социальная сеть обмена дневниками, в которой реализованны механизмы авторизации, администрирования, есть возможность подписаться на любимых авторов и оставить коментарий под каждым из постов, посты можно добавлять/удалять/исправлять (только автору или админу), к каждому из постов можно добавить картинку. Кроме того главные страницы закешированны, чтобы снизить нагрузку на БД.

### Полезные ссылки:

Мой [LinkedIn](https://www.linkedin.com/in/andrei-shchiptsov-037369267/https://www.linkedin.com/in/andrei-shchiptsov-037369267/) для вопросов и предложений

Ознакомиться с проектом можно тут: [YaTube](http://ruzzik.pythonanywhere.com/)

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Bigbrotherx/hw05_final
```

```
cd hw05_finalhw05_final
```

Cоздать и активировать виртуальное окружение:

```
python3.9 -m venv env
```

* Если у вас Linux/macOS

  ```
  source env/bin/activate
  ```
* Если у вас windows

  ```
  source env/scripts/activate
  ```

```
python3.9 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```
