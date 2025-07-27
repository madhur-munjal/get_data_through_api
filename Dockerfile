FROM python:3.11-slim

WORKDIR /src
COPY requirements.txt .
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    python3-dev

RUN pip install -r requirements.txt

COPY ./src /src
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]