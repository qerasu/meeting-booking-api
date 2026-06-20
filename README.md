# Bookings API

## macos/linux

### Запуск

```bash
cp .env.example .env
docker-compose up --build
```

API будет доступно по адресу: `http://localhost:8000`

Эндпоинты:

```text
POST /bookings
GET /bookings/{id}
GET /bookings?status=pending&limit=20&offset=0
DELETE /bookings/{id}
```

## Windows

### Запуск

```powershell
copy .env.example .env
docker compose up --build
```

После запуска откройте `http://localhost:8000/docs`.

### Тесты

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest
```

Пример создания брони:

```bash
curl -X POST http://localhost:8000/bookings \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","datetime":"2026-06-21T10:00:00+00:00","service_type":"consultation"}'
```

### Тесты

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m pytest
```

## Технические решения

FastAPI выбран для REST API и валидации входных данных через Pydantic.
SQLAlchemy используется как ORM, миграции выполняются через Alembic.
Celery обрабатывает брони асинхронно через Redis broker/result backend.
Идемпотентность воркера обеспечена обновлением только записей со статусом `pending`.