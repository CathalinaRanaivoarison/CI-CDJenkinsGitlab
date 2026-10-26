FROM python:3.14-slim

RUN useradd appuser 

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

USER appuser

CMD ["gunicorn","-c","gunicorn.conf.py","main:app"]