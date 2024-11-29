FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Exponer el puerto en el que Flask o Gunicorn correrá
EXPOSE 8080

# Comando para correr la aplicación
# Usamos Gunicorn en lugar del servidor de desarrollo de Flask para producción
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "flaskr.app:app", "--workers", "3"]
