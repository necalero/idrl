# Utiliza una imagen base de Python
FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos del proyecto a la imagen
COPY . /app

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto de Celery (si deseas monitorear, no obligatorio)
EXPOSE 5001

# Comando para iniciar Celery y el servicio Flask si lo necesitas
CMD ["celery", "-A", "app.celery", "worker", "--loglevel=info"]
