# Dockerfile

FROM python:3.12-slim

# Рабочая директория
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libsqlite3-dev \
    tk-dev \
    libxml2-dev \
    libxslt1-dev \
    libbz2-dev \
    libcurl4-openssl-dev \
    pkg-config \
    libffi-dev \
    gcc \
    make \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*


# Копируем требования и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальную часть проекта
COPY . .

# Запускаем приложение
CMD ["python", "main.py"]