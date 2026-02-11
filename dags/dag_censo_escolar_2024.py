# dags/dag_censo_escolar_2024.py
import pendulum
import pandas as pd
import json
from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy import text

from sqlalchemy.dialects.postgresql import JSONB

# Caminho onde o Docker mapeou nossa pasta 'data'
RAW_DATA_PATH = '/opt/airflow/data/censo_escolar_2024.csv'
RESULTS_TABLE_NAME = 'censo_escolar_resumo_2024'

def _extract_data():
    """Lê o arquivo CSV bruto do Censo Escolar."""
    print(f"Iniciando extração do arquivo: {RAW_DATA_PATH}")
    df = pd.read_csv(
        RAW_DATA_PATH,
        sep=';',
        encoding='latin-1',
        low_memory=False
    )
    print(f"Extração concluída. {len(df)} linhas carregadas.")
    return df

def _transform_data(ti):
    """Executa as 16 transformações solicitadas, ATUALIZADAS para o Censo 2024."""
    df = ti.xcom_pull(task_ids="extract")
    results = {}
    total_escolas = len(df)

    print("Iniciando transformações (v3)...")

    # 1 & 2: Qtd e % por dependência
    dep_counts = df['TP_DEPENDENCIA'].value_counts()
    results['qtd_por_dependencia'] = dep_counts.to_dict()
    results['pct_por_dependencia'] = (dep_counts / total_escolas * 100).round(2).to_dict()

    # 3: Qtd e % de escolas privadas por categoria
    df_privada = df[df['TP_DEPENDENCIA'] == 4] # 4 = Privada
    cat_privada_counts = df_privada['TP_CATEGORIA_ESCOLA_PRIVADA'].value_counts()
    results['qtd_categoria_privada'] = cat_privada_counts.to_dict()
    results['pct_categoria_privada'] = (cat_privada_counts / len(df_privada) * 100).round(2).to_dict()
    
    # 4, 5, 6, 7: Qtd e % por zona de localização
    loc_counts = df['TP_LOCALIZACAO'].value_counts()
    qtd_urbana = int(loc_counts.get(1, 0))
    qtd_rural = int(loc_counts.get(2, 0))
    results['qtd_zona_urbana'] = qtd_urbana
    results['qtd_zona_rural'] = qtd_rural
    results['pct_zona_urbana'] = round((qtd_urbana / total_escolas * 100), 2)
    results['pct_zona_rural'] = round((qtd_rural / total_escolas * 100), 2)

    # 8: Qtd em assentamento
    results['qtd_em_assentamento'] = int(df[df['TP_LOCALIZACAO_DIFERENCIADA'] == 2].shape[0])

    # 9: Qtd por situação de funcionamento
    sit_counts = df['TP_SITUACAO_FUNCIONAMENTO'].value_counts()
    results['qtd_situacao_funcionamento'] = sit_counts.to_dict()

    # 10: Mês de início e término do ano letivo
    df['DT_ANO_LETIVO_INICIO'] = pd.to_datetime(df['DT_ANO_LETIVO_INICIO'], errors='coerce')
    df['DT_ANO_LETIVO_TERMINO'] = pd.to_datetime(df['DT_ANO_LETIVO_TERMINO'], errors='coerce')
    results['contagem_mes_inicio_letivo'] = df['DT_ANO_LETIVO_INICIO'].dt.month.value_counts().to_dict()
    results['contagem_mes_termino_letivo'] = df['DT_ANO_LETIVO_TERMINO'].dt.month.value_counts().to_dict()
    
    # 11: % por forma de ocupação do prédio
    ocup_counts = df['TP_OCUPACAO_PREDIO_ESCOLAR'].value_counts()
    results['pct_forma_ocupacao_predio'] = (ocup_counts / total_escolas * 100).round(2).to_dict()

    # 12: Qtd que funcionam na casa do professor
    results['qtd_casa_do_professor'] = 0 # Coluna removida no Censo 2024

    # 13: Qtd e % com água potável
    com_agua = int(df[df['IN_AGUA_POTAVEL'] == 1].shape[0])
    results['qtd_com_agua_potavel'] = com_agua
    results['pct_com_agua_potavel'] = round((com_agua / total_escolas * 100), 2)

    # 14: Qtd e % sem abastecimento de água
    sem_agua = int(df[df['IN_AGUA_INEXISTENTE'] == 1].shape[0])
    results['qtd_sem_abastecimento_agua'] = sem_agua
    results['pct_sem_abastecimento_agua'] = round((sem_agua / total_escolas * 100), 2)
    
    # 15: Qtd e % sem esgoto por estado
    sem_esgoto = df[df['IN_ESGOTO_INEXISTENTE'] == 1]
    sem_esgoto_por_uf = sem_esgoto.groupby('SG_UF')['CO_ENTIDADE'].count()
    total_escolas_por_uf = df.groupby('SG_UF')['CO_ENTIDADE'].count()
    pct_sem_esgoto_por_uf = (sem_esgoto_por_uf / total_escolas_por_uf * 100).round(2).fillna(0)
    results['qtd_sem_esgoto_por_uf'] = sem_esgoto_por_uf.to_dict()
    results['pct_sem_esgoto_por_uf'] = pct_sem_esgoto_por_uf.to_dict()

    # 16: Qtd e % sem banheiro
    com_banheiro = df[df['IN_BANHEIRO'] == 1].shape[0]
    sem_banheiro = total_escolas - com_banheiro
    results['qtd_sem_banheiro'] = int(sem_banheiro)
    results['pct_sem_banheiro'] = round((sem_banheiro / total_escolas * 100), 2)

    print("Transformações concluídas.")
    return json.loads(json.dumps(results, default=int))


# Cole esta função no lugar da antiga _load_data
def _load_data(ti):
    """Carrega o dicionário de resultados em uma tabela no Postgres. [VERSÃO FINAL CORRIGIDA]"""
    results_dict = ti.xcom_pull(task_ids="transform")
    hook = PostgresHook(postgres_conn_id="postgres_local_db")
    engine = hook.get_sqlalchemy_engine()

    print(f"Iniciando carregamento para a tabela {RESULTS_TABLE_NAME}...")

    records_to_insert = []
    for key, value in results_dict.items():
       
        records_to_insert.append({
            'metrica': key,
            'valor': value
        })
    
    df_results = pd.DataFrame(records_to_insert)

    with engine.connect() as conn:
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {RESULTS_TABLE_NAME} (
                metrica VARCHAR(255) PRIMARY KEY,
                valor JSONB,
                ultima_atualizacao TIMESTAMPTZ
            );
        """))
        conn.execute(text(f"TRUNCATE TABLE {RESULTS_TABLE_NAME};"))
        
        df_results.to_sql(
            RESULTS_TABLE_NAME,
            conn,
            if_exists='append',
            index=False,
            dtype={'valor': JSONB} 
        )
        
        conn.execute(text(f"UPDATE {RESULTS_TABLE_NAME} SET ultima_atualizacao = NOW();"))
       
    
    print("Carregamento concluído com sucesso.")


with DAG(
    dag_id="pipeline_censo_escolar_2024",
    start_date=pendulum.datetime(2024, 1, 1, tz="America/Sao_Paulo"),
    schedule=None,
    catchup=False,
    tags=["censo_escolar", "inep", "producao"],
) as dag:
    extract_task = PythonOperator(
        task_id="extract",
        python_callable=_extract_data,
    )

    transform_task = PythonOperator(
        task_id="transform",
        python_callable=_transform_data,
    )

    load_task = PythonOperator(
        task_id="load",
        python_callable=_load_data,
    )

    extract_task >> transform_task >> load_task