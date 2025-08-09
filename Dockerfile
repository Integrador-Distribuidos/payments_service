# Use a imagem oficial do Python
FROM python:3.10

# Define variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Cria e define o diretório de trabalho
WORKDIR /code

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências do Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia o projeto para o container
COPY . .
RUN python manage.py collectstatic --noinput
# Comando padrão (pode ser sobrescrito no docker-compose)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "payments.wsgi:application"]
