# Fitness Training Diary (Telegram Mini App)

>Важно!
>Значительная часть проекта (fronend, backend, telgram) сгенерирована с помощью AI.
>Основная цель проекта прокачака и демонстрация своих DevOps-навыков, таких как docker, CI/CD, k8s.
>Не рекомендуется для работы в prod среде!

## Архитектура проекта

Проект состоит из 4 компонентов:

- `frontend` — React + Vite (UI Telegram Mini App)
- `backend` — FastAPI (REST API, авторизация, бизнес-логика)
- `db` — PostgreSQL (хранение пользователей, шаблонов, сессий, метрик)
- `telegram` — отдельный Python-сервис для Telegram-уведомлений/бот-логики (опционально)

### Взаимодействие компонентов

1. Пользователь открывает Mini App в Telegram.
2. `frontend` получает `initData` от Telegram WebApp SDK.
3. `frontend` отправляет запросы в `backend` (`/api/v1/...`) и передаёт `initData`.
4. `backend` проверяет подпись Telegram (`hash`) по `TELEGRAM_BOT_TOKEN`.
5. `backend` читает/пишет данные в PostgreSQL.
6. `telegram`-сервис (если запущен) может отправлять сообщения через Bot API.

Схема потока:

```text
Telegram Client
    -> Frontend (Mini App UI)
    -> Backend API (FastAPI)
    -> PostgreSQL

Telegram Service (optional) -> Telegram Bot API
```

## Режимы работы: prod и dev

### Prod-режим (`docker-compose.yml`)

Используется для максимально приближённого к боевому окружения:

- `frontend` собирается в статические файлы и отдаётся через Nginx (`:8080`)
- `backend` работает без hot-reload
- `db` работает в отдельном контейнере
- `telegram` сервис подключён в compose

Запуск:

```bash
docker compose up --build
```

Адреса:
- Frontend: `http://localhost:8080`
- Backend: `http://localhost:8000` (`/docs`)
- Postgres: `localhost:5432`

### Dev-режим (`docker-compose.dev.yml`)

Используется для локальной разработки:

- `frontend` поднимается как Vite dev server (`:5173`)
- `backend` запускается с `--reload` (auto-reload)
- исходники `frontend` и `backend` монтируются как volume
- упрощён dev-auth через заголовок `X-Dev-Telegram-Id` (при `DEBUG=true`)

Запуск:

```bash
docker compose -f docker-compose.dev.yml up
```

Адреса:
- Frontend (Vite): `http://localhost:5173`
- Backend: `http://localhost:8000` (`/docs`)
- Postgres: `localhost:5432`

Важно для dev:
- при запуске в обычном браузере (вне Telegram) фронт отправляет `X-Dev-Telegram-Id`
- backend принимает этот заголовок только в режиме `DEBUG=true`

## Быстрый старт (Docker)

### Makefile (короткие команды)

В корне проекта доступен `Makefile` с удобными алиасами для Docker Compose:

```bash
make help

# prod
make up
make down
make build
make logs

# dev
make up-dev
make down-dev
make build-dev
make logs-dev

# утилиты
make ps
make ps-dev
make restart
make restart-dev
make clean
make db-only
```

1) Создай `.env` по примеру:

```bash
cp .env.example .env
```

2) Укажи `TELEGRAM_BOT_TOKEN` в `.env`.

3) Запусти:

```bash
make up
```

- Frontend: `http://localhost:8080`
- Backend: `http://localhost:8000` (OpenAPI: `http://localhost:8000/docs`)
- Postgres: `localhost:5432`

## Режим разработки (dev)

### Вариант A: dev в Docker

В корне проекта:

```bash
make up-dev
```

Что получишь:
- Postgres: `localhost:5432`
- Backend (с авто‑перезагрузкой): `http://localhost:8000` (`/docs`)
- Frontend (Vite dev‑server): `http://localhost:5173`

Код backend и frontend монтируется в контейнеры через volume, так что изменения в файлах сразу подхватываются.

Чтобы тестировать **в обычном браузере** (не внутри Telegram), dev-режим использует заголовок
`X-Dev-Telegram-Id` (работает только при `DEBUG=true` на backend). В `docker-compose.dev.yml`
он включён автоматически через `VITE_DEV_TELEGRAM_ID=1`.

### Вариант B: локально (без Docker для кода)

1) База данных (через Docker)

В отдельном терминале в корне проекта:

```bash
docker compose up db
```

Postgres станет доступен на `localhost:5432`.

2) Backend (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# миграции
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/fitness_diary"
alembic upgrade head

# запуск API с авто‑перезагрузкой
uvicorn app.main:app --reload --port 8000
```

Теперь backend доступен по `http://localhost:8000` (`/docs` для Swagger).

3) Frontend (Vite + React)

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

По умолчанию frontend ходит к `http://localhost:8000/api/v1`, так что ничего дополнительно настраивать не нужно.
- Открывай UI по адресу: `http://localhost:5173` в браузере.

## Telegram Auth

Frontend автоматически отправляет:
- `POST /api/v1/auth/telegram` с `init_data` (Telegram WebApp initData)
- и прикрепляет `X-Telegram-Init-Data` ко всем запросам

Backend валидирует `hash` из initData по токену бота.

## Как создать Mini App в Telegram

1) **Создай бота через BotFather**
- Найди `@BotFather` в Telegram.
- Отправь команду `/newbot` и следуй инструкциям.
- Скопируй `BOT_TOKEN` и вставь его в `.env` как `TELEGRAM_BOT_TOKEN`.

2) **Задай домен Mini App (когда будет прод‑URL фронтенда)**
- В `@BotFather` отправь:
  - `/setdomain`
  - выбери своего бота
  - укажи URL, где доступен фронтенд Mini App, например: `https://my-fitness-app.example.com`

3) **Добавь Web App‑кнопку в меню бота**
- В `@BotFather` отправь:
  - `/setmenubutton`
  - выбери бота
  - выбери тип **Web App**
  - задай:
    - **Button text** — например: `Тренировочный дневник`
    - **Web App URL** — тот же URL фронтенда (`https://...`)

4) **(Опционально) Кнопка Web App в сообщении**
- В коде твоего серверного бота можно отправлять сообщение с `reply_markup` вида:

```json
{
  "reply_markup": {
    "inline_keyboard": [
      [
        {
          "text": "Открыть дневник",
          "web_app": { "url": "https://my-fitness-app.example.com" }
        }
      ]
    ]
  }
}
```

После этого при открытии Mini App внутри Telegram будет передаваться `initData`, которое backend уже умеет проверять.
