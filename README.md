# Сайт для рецептов Foodgram (Recipe Website Foodgram)

## Описание проекта (Project Description):

### Краткое описание (Brief Description):

####ru
Проект Foodgram позволяет вам создавать, просматривать и добавлять в избранное кулинарные рецепты. Поддерживает возможности фильтрации по тегам и составления списка покупок.

####en
The Foodgram project allows you to create, view, and favorite culinary recipes. It supports filtering by tags and generating shopping lists.

### Использованные технологии:

####ru
Бэкенд написан с использованием следующих технологий:

####en
Backend developed using the following technologies

- Python 3.10, Django 3.2.3, DjangoRestFramework 2.12.4

####ru
Фронтенд написан с использованием следующих технологий:

####en
Frontend developed using

- javascript, HTML

####ru
Запуск проекта осуществляется с помощью nginx и docker

####en
The project is deployed using Nginx and Docker


## Ссылка на проект (Project Link):

http://myuniquehotsname.zapto.org

## Подробности запуска (Launch Details):

### Как запустить проект (How to Launch the Project):

####ru
Клонировать репозиторий(если используется docker-compose.yml) и перейти в него в командной строке или скопировать только файл docker-compose.production.yml:

####en
Clone the repository (if using docker-compose.yml) and navigate into it via the command line, or copy only the docker-compose.production.yml file:

```
git clone https://github.com/balahoncevg/foodgram.git
```

```
cd foodgram
```

####ru
Выполнить последовательно команды:

Примечание:
для запуска можно использовать файлы docker-compose.production.yml(как в примере) и docker-compose.yml

####en
Run the following commands in sequence:

Note:
To launch the project, you can use either docker-compose.production.yml (as shown in the example) or docker-compose.yml

```
sudo docker compose -f docker-compose.production.yml pull
sudo docker compose -f docker-compose.production.yml down
sudo docker compose -f docker-compose.production.yml up -d
```

####ru
Выполнить миграции и собрать статические файлы:

####en
Run migrations and collect static files:

```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/backend_static/. /backend_static/static/
```

### Различия между docker-compose.yml и docker-compose.production.yml:

docker-compose.yml позволяет создавать docker образы на основе файлов пректа. Подходит для запуска с устройства, на котором есть копия проекта. Используется для разработки - внесения изменений и исправлений.

docker-compose.production.yml создана для использования на удаленном сервере. Не создает docker образы, а загружает их с DockerHub, не использует локальные файлы пректа. Подходит для пользовательского запуска

### Differences Between docker-compose.yml and docker-compose.production.yml:

docker-compose.yml creates Docker images based on project files. Suitable for local development with the project copied to your device. Used for making updates or debugging.

docker-compose.production.yml is designed for use on remote servers. It doesn't build Docker images but pulls them from DockerHub. It does not rely on local project files and is intended for end-user deployment.

## Использование (Usage):

####ru
Для полноценного использования пректа необходимо зарегестрироваться на сайте (создать логи и пароль). После этого ползователю станут доступны возможности создавать рецепты и списки избранного. для создания рецепта необходимо нажать на кнопку "Добавить рецепт", после чего указать необходимые данные. Созданые рецепты можно удалать и редактировать.

####en
To fully utilize the project, register on the site (create a login and password). After registration, users can create recipes and favorite lists. To create a recipe, click the "Add Recipe" button and enter the required details. Created recipes can be deleted or edited.


## Об авторе (About the Author):

####ru
Студент Яндекс.Практикума на направлении Python Backend

####en
A Yandex.Practicum student specializing in Python Backend development
