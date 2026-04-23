# 🚀 Space Mission Monitoring

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-blue)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11-green)](https://python.org/)
[![Docker](https://img.shields.io/badge/Docker-ready-blue)](https://docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**Система мониторинга космических миссий** — бэкенд для отслеживания состояния систем космического корабля (двигатели, жизнеобеспечение, связь) с поддержкой WebSocket-уведомлений в реальном времени, датчиков с граничными значениями и JWT-авторизации.

## 📋 Содержание

- [Возможности](#-возможности)
- [Технологии](#-технологии)
- [Быстрый старт](#-быстрый-старт)
- [API Endpoints](#-api-endpoints)
- [WebSocket](#-websocket)
- [Тестирование](#-тестирование)
- [Структура проекта](#-структура-проекта)
- [Автор](#-автор)

## ✨ Возможности

- **JWT авторизация** (Argon2 хеширование паролей)
- **Управление системами** (двигатели, жизнеобеспечение, связь)
- **Датчики с граничными значениями** — автоматическая генерация warning/recover
- **WebSocket с комнатами** — подписка на события конкретной системы
- **Пагинация, сортировка, фильтрация** для списка систем
- **Rate limiting** (5 запросов в минуту на создание систем)
- **Docker + docker-compose** (PostgreSQL, Redis, бэкенд)
- **Allure-ready** (подготовлено для генерации отчётов)

## 🛠 Технологии

| Компонент | Технология |
|-----------|------------|
| **Фреймворк** | FastAPI |
| **ORM** | SQLAlchemy |
| **База данных** | PostgreSQL |
| **Кэш / WebSocket** | Redis |
| **Авторизация** | JWT + Argon2 |
| **Контейнеризация** | Docker / docker-compose |
| **Лимиты запросов** | slowapi |

## 🚀 Быстрый старт

### Требования

- Docker
- Docker Compose

### Запуск

```bash
# Клонировать репозиторий
git clone https://github.com/Anna1327/space-mission-monitoring.git
cd space-mission-monitoring

# Запустить контейнеры
docker-compose up --build
После запуска сервер доступен по адресу: http://localhost:8000

Документация API
Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc
```

## 📡 API Endpoints

### Авторизация

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/api/v1/auth/register` | Регистрация клиента |
| POST | `/api/v1/auth/token` | Получение JWT токена |

### Системы

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/api/v1/systems/` | Список систем (пагинация, сортировка, фильтрация) |
| GET | `/api/v1/systems/{id}` | Получить систему по ID |
| POST | `/api/v1/systems/` | Создать систему (rate limit: 5/мин) |
| POST | `/api/v1/systems/{id}/trigger/{event}` | Триггер события (failure/warning/recover) |

### Датчики

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/api/v1/systems/{id}/sensors/` | Получить все датчики системы |
| POST | `/api/v1/systems/{id}/sensors/` | Создать датчик |
| PATCH | `/api/v1/systems/{id}/sensors/{sensor_id}/value` | Обновить показания (авто-триггер warning/recover) |

### Health Check

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/health` | Быстрая проверка |
| GET | `/health/detailed` | Детальная проверка (БД, Redis, WebSocket) |

## 🔌 WebSocket

Подключение к WebSocket с подпиской на события системы:

```javascript
const ws = new WebSocket("ws://localhost:8000/api/v1/ws/1");
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## 🧪 Тестирование

Тесты вынесены в отдельный репозиторий: [space-mission-tests](https://github.com/Anna1327/space-mission-tests)

- API тесты (pytest)
- WebSocket тесты
- Тесты датчиков с граничными значениями
- SSH-туннель для проверки БД

### 📁 Структура проекта
```text
space-mission-monitoring/
├── app/
│   ├── api/           # Эндпоинты (v1, health)
│   ├── core/          # Конфиги, безопасность, БД
│   ├── models/        # SQLAlchemy модели
│   ├── schemas/       # Pydantic схемы
│   ├── services/      # Бизнес-логика
│   └── utils/         # WebSocketManager
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```
### 👤 Автор
Anna1327 — GitHub

⭐ Если тебе понравился проект, поставь звезду!
