# Rest API Aiohttp

API приложение для создания, обновления, получения, удаления объявлений.

## Функционал

- Валидация входящих данных
- Регистрация и аутентификация
- CRUD операции по объявлениям
- Удалять, обновлять объявления может только владелец объявления
- Хэширование паролей
- Миграции

## Начало работы

1. Для работы необходимо установить [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Собрать образ с помощью команды ```docker build -t image_aiohttp: 1.0 .```
3. Запустить образ командой ```docker-compose up -d```

## Стэк

- Aiohttp
- PostgreSQL
- Pydantic
- SQLAlchemy
- Bcrypt
- Alembic
- Logging
- PyJWT