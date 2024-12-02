# Utilizar una imagen de Python
FROM python:3.11-slim

# Establecer el directorio del contendor
WORKDIR /app
# Copiar el archivo requirements.txt primero (para aprovechar la caché de Docker)

COPY requirements.txt /app
# Instalar las dependencias desde requirements.txt

RUN pip install -r requirements.txt
# Copiamos los archivos al directorio del contenedor

COPY . /app
# Exponer el puerto en el que la aplicación está corriendo en el contenedor

EXPOSE 8000
# Comando para ejecutar la aplicación
# CMD ["python", "app_model.py"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]