# Manual do Ambiente - Serviço de Pagamentos

### 1. Visão Geral
Este manual tem como objetivo fornecer instruções detalhadas para configurar, executar e manter o ambiente do Serviço de Pagamentos. O serviço é responsável por gerenciar transações de pagamento, gerar relatórios de vendas, e integrar com APIs externas para processamento de pagamentos.
<hr>

### 2. Requisitos de Sistema
Antes de começar a configurar o ambiente, certifique-se de que você tem os seguintes requisitos de sistema instalados:

- Docker (para containers e orquestração)

- IDE como VS Code

- Postman (para testar APIs)
<hr>

### 3. Configuração do Ambiente Local

 #### 3.1. Instalação das Dependências

 Para começar a configurar o ambiente local, siga os passos abaixo:
 
```bash 
git clone https://github.com/Integrador-Distribuidos/payments_service.git
cd payments_service
```

Execute o comando para iniciar os containers

```bash 
docker-compose up --build -d
```
```--build```: Força a reconstrução das imagens antes de iniciar os containers.

```-d```: Inicia os containers em segundo plano (detached mode), permitindo que o terminal seja liberado.

<hr>

### 4. Crie e configure o arquivo ```.env```:

O arquivo ```.env``` é onde você configurará as variáveis de ambiente necessárias para o funcionamento da aplicação, como as credenciais do banco de dados e a chave da API do **Asaas**(colocar a chave do asaas entre aspas simples ').

```bash 
# Database
POSTGRES_DB=pagamentos
POSTGRES_USER=postgres
POSTGRES_PASSWORD=root
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Defina a URL do banco de dados usando as variáveis acima
DATABASE_URL=postgres://postgres:root@db:5432/pagamentos

# Asaas
ASAAS_API_KEY='Sua-chave-API-aqui'
```

- ```POSTGRES_DB```: Nome do banco de dados (exemplo: pagamentos).

- ```POSTGRES_USER```: Usuário do banco de dados (geralmente postgres).

- ```POSTGRES_PASSWORD```: Senha do banco de dados (por exemplo, root).

- ```POSTGRES_HOST```: Nome do serviço de banco de dados no Docker Compose (deve ser db).

- ```POSTGRES_PORT```: Porta do banco de dados (padrão 5432).

- ```DATABASE_URL```: URL de conexão completa para o banco de dados.

- ```ASAAS_API_KEY```: Chave da API para autenticar no serviço do Asaas. Substitua "Sua-chave-API-aqui" pela chave fornecida pelo Asaas.

<hr>

### 5. Estrutura do docker-compose.yml

Um exemplo de como o arquivo docker-compose.yml pode ser configurado para os serviços:

```bash
version: '3'
services:
  payment-service:
    image: node:14
    container_name: payment-service
    working_dir: /app
    volumes:
      - .:/app
    ports:
      - "3000:3000"
    environment:
      - POSTGRES_HOST=db
      - POSTGRES_PORT=5432
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=root
      - POSTGRES_DB=pagamentos
    command: npm run dev

  db:
    image: postgres:12
    container_name: payment-db
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=root
      - POSTGRES_DB=pagamentos
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:

```

```payment-service```: Este é o seu serviço de pagamentos. Ele está configurado para rodar um container Node.js e conectar ao banco de dados PostgreSQL.

```db```: Este é o container do banco de dados PostgreSQL, configurado para usar o banco pagamentos com as credenciais fornecidas no arquivo .env.

Volumes: O volume ```pgdata``` garante que os dados do banco de dados sejam persistidos, mesmo que o container seja removido.

<hr>

### 6. Resolução de Problemas Comuns
#### 6.1. Erro de Conexão ao Banco de Dados:

- Verifique se o banco de dados PostgreSQL está em execução. Você pode usar o comando ```docker-compose ps``` para ver o status dos containers.

- Verifique se as variáveis de ambiente no ```.env``` estão corretas e correspondem à configuração no Docker Compose.

 #### 6.2. Erro de Conexão com o Asaas:

- Verifique se a chave API do Asaas está configurada corretamente no arquivo ```.env```.

- Certifique-se de que a API do **Asaas** está funcionando corretamente.

#### 6.3. Erro ao Rodar o Serviço:

- Caso o serviço não esteja iniciando, verifique os logs com ```docker-compose logs``` para identificar o que pode estar causando o erro.

<hr>

### 7. Conclusão

Este **Manual do Ambiente** fornece as instruções necessárias para configurar e executar o Serviço de **Pagamentos** localmente, com o banco de dados PostgreSQL e a integração com a API do ```Asaas```.

