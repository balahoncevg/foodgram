# Сайт для рецептов Foodgram

## Описание проекта:

### Краткое описание:

Проект Foodgram позволяет вам создавать, просматривать и добавлять в избранное кулинарные рецепты. Поддерживает возможности фильтрации по тегам и составления списка покупок.

### Использованные технологии:

Бэкенд написан с использованием следующих технологий:

Python 3.10, Django 3.2.3, DjangoRestFramework 2.12.4

Фронтенд написан с использованием следующих технологий:

javascript, HTML

Запуск проекта осуществляется с помощью nginx и docker

## Ссылка на проект:

http://myuniquehotsname.zapto.org

## Подробности запуска:

### Как запустить проект:

Клонировать репозиторий(если используется docker-compose.yml) и перейти в него в командной строке или скопировать только файл docker-compose.production.yml:

```
git clone https://github.com/balahoncevg/foodgram.git
```

```
cd foodgram
```

Выполнить последовательно команды:

Примечание:
для запуска можно использовать файлы docker-compose.production.yml(как в примере) и docker-compose.yml

```
sudo docker compose -f docker-compose.production.yml pull
sudo docker compose -f docker-compose.production.yml down
sudo docker compose -f docker-compose.production.yml up -d
```

Выполнить миграции и собрать статические файлы:

```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/backend_static/. /backend_static/static/
```

### Различия между docker-compose.yml и docker-compose.production.yml:

docker-compose.yml позволяет создавать docker образы на основе файлов пректа. Подходит для запуска с устройства, на котором есть копия проекта. Используется для разработки - внесения изменений и исправлений.

docker-compose.production.yml создана для использования на удаленном сервере. Не создает docker образы, а загружает их с DockerHub, не использует локальные файлы пректа. Подходит для пользовательского запуска

## Использование:

Для полноценного использования пректа необходимо зарегестрироваться на сайте (создать логи и пароль). После этого ползователю станут доступны возможности создавать рецепты и списки избранного. для создания рецепта необходимо нажать на кнопку "Добавить рецепт", после чего указать необходимые данные. Созданые рецепты можно удалать и редактировать.

## Об авторе:

Студент Яндекс.Практикума на направлении Python Backend
