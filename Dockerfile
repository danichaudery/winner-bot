FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential libffi-dev && rm -rf /var/lib/apt/lists/*

COPY bot/requirements.txt /app/bot/requirements.txt
RUN python -m pip install --upgrade pip && pip install -r /app/bot/requirements.txt

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "bot.app:app", "--host", "0.0.0.0", "--port", "8000"]

