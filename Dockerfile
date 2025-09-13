# Usa una imagen oficial de Python como imagen base
FROM python:3.12-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo de dependencias al directorio de trabajo
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación al directorio de trabajo
COPY . .

# Expone el puerto en el que se ejecuta la aplicación
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
