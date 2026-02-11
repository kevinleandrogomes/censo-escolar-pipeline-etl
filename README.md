# Pipeline ETL: Microdados Censo Escolar 2024 📊

## 🎯 Objetivo
Este projeto automatiza a extração e o processamento de grandes volumes de dados do INEP, transformando-os em métricas educacionais estratégicas através de uma arquitetura moderna de engenharia de dados.

## 🏗️ Arquitetura e Tecnologias
* **Linguagem Principal:** Python (Pandas) para limpeza e transformação.
* **Orquestração:** Apache Airflow gerindo o workflow de dados.
* **Conteinerização:** Docker e Docker Compose para isolamento total do ambiente.
* **Armazenamento:** PostgreSQL como Data Warehouse.
* **Visualização:** Metabase para criação de dashboards estratégicos.
  [![Metabase](https://img.shields.io/badge/Metabase-509EE3?style=for-the-badge&logo=Metabase&logoColor=white)](https://www.metabase.com/)
## 📈 Métricas Processadas
O pipeline calcula automaticamente **indicadores-chave**, com foco em:
* **Infraestrutura Tecnológica**: Acesso a internet banda larga, Wi-Fi e disponibilidade de tablets/computadores.
* **Acessibilidade (PCD)**: Escolas com dependências acessíveis e banheiros adaptados.
* **Recursos Humanos**: Nível de qualificação e formação docente.
* **Espaços de Aprendizado**: Presença de laboratórios de informática, ciências e bibliotecas.

## 📁 Sobre os Dados
Devido ao limite de tamanho do GitHub, o arquivo bruto `censo_escolar_2024.csv` não está incluído neste repositório. 
Para rodar o pipeline:
1. Baixe os microdados no portal oficial do INEP.
2. Coloque o arquivo `.csv` dentro da pasta `/data` antes de iniciar os containers.

## 🚀 Como Executar
1. Certifique-se de ter o Docker instalado.
2. Clone este repositório.
3. Execute `docker-compose up -d`.
4. Acesse o Airflow em `localhost:8080` e o Metabase em `localhost:3000`.
