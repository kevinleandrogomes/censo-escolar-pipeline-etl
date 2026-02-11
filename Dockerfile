# Use a imagem oficial do Airflow como nossa base
FROM apache/airflow:2.9.2

# Mude para o usuário root para instalar pacotes de sistema, se necessário
USER root

# Instala algumas dependências do sistema (boa prática)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Mude de volta para o usuário airflow
USER airflow

# Instale nossas bibliotecas Python necessárias
RUN pip install --no-cache-dir pandas sqlalchemy psycopg2-binary apache-airflow-providers-postgres