FROM python:3.11-slim

#ENV PYTHONUNBUFFERED=1
#ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /src
COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
#    default-mysql-client \
    redis-server \
    build-essential \
    default-libmysqlclient-dev \
    python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*




RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini .
COPY alembic/ alembic/

COPY ./src /src
EXPOSE 8000
CMD ["/bin/sh", "-c", "sleep 20 && redis-server --daemonize yes && uvicorn main:app --host 0.0.0.0 --port 8000"]