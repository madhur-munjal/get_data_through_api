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


RUN pip install -r requirements.txt

COPY ./src /src
RUN ls -la /src

RUN chmod +x start.sh
#ENTRYPOINT ["./start.sh"]
# Run Alembic migrations, then start Uvicorn
#CMD /bin/bash -c "uvicorn main:app --host 0.0.0.0 --port 8000 && alembic upgrade head"
CMD redis-server --daemonize yes && uvicorn main:app --host 0.0.0.0 --port 8000

#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
##CMD ["fastapi", "dev", "main.py", "--host", "0.0.0.0", "--port", "8000"]
