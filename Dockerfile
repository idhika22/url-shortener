FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY shortener ./shortener

COPY wsgi.py .

RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8000

CMD ["gunicorn","--bind","0.0.0.0:8000","wsgi:app"]
