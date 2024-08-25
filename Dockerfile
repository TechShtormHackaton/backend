FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y libgl1-mesa-glx

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


RUN mkdir -p /app/static

EXPOSE 8000

CMD ["bash", "-c", "alembic upgrade head && uvicorn app:app --host 0.0.0.0 --port 8000"]
