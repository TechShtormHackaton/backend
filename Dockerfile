FROM python:3.10

WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/static

EXPOSE 8000

CMD ["bash", "-c", "alembic upgrade head && uvicorn app:app --host 0.0.0.0 --port 8000"]
