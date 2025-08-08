FROM python:3.11-slim

WORKDIR /src
COPY requirements.txt .
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    python3-dev

RUN pip install -r requirements.txt

COPY ./src /src
RUN ls -la /src

# Run Alembic migrations, then start Uvicorn
CMD /bin/bash -c "uvicorn main:app --host 0.0.0.0 --port 8000 && alembic upgrade head"

#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
##CMD ["fastapi", "dev", "main.py", "--host", "0.0.0.0", "--port", "8000"]
