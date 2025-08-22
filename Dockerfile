FROM python:3.11-slim

#ENV PYTHONUNBUFFERED=1
#ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /src
COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y redis-server && \
    apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    python3-dev


RUN pip install --no-cache-dir -r requirements.txt

COPY ./src /src
EXPOSE 8000
CMD ["/bin/sh", "-c", "redis-server --daemonize yes && uvicorn main:app --host 0.0.0.0 --port 8000"]
