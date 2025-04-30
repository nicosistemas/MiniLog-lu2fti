# Usamos una imagen oficial de Python
FROM python:3.11-slim

# Crear el directorio de la aplicación
WORKDIR /app

# Copiar los archivos de requerimientos e instalar
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Exponer el puerto en el que corre Flask
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]