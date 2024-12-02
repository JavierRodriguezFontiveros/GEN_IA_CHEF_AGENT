# Etapa 1: Imagen base de Python
FROM python:3.12.7-slim

# Etapa 2: Configuración del directorio de trabajo
WORKDIR /app

# Etapa 3: Copiar los archivos necesarios
# Copiar el archivo requirements.txt primero para aprovechar la caché de Docker
COPY requirements.txt /app/

# Instalar las dependencias de Python
RUN pip install -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . /app/

# Etapa 4: Exponer el puerto que usará FastAPI
EXPOSE 8000

# Etapa 5: Definir el comando para ejecutar la aplicación
CMD ["uvicorn", "app:app", "--host", "0.0.0.0"]
