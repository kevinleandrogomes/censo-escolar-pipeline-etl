import pandas as pd
import sys

# O caminho para o seu arquivo CSV, relativo a este script
# (Como o CSV está na pasta 'data')
caminho_do_arquivo = 'data/censo_escolar_2024.csv' 

print(f"Lendo apenas o cabeçalho do arquivo: {caminho_do_arquivo}...")

try:
    # Lê apenas as 5 primeiras linhas para pegar os nomes das colunas
    # Isso é super rápido e não usa quase nada de memória.
    df_amostra = pd.read_csv(
        caminho_do_arquivo, 
        sep=';', 
        encoding='latin-1',
        nrows=5 
    )
    
    print("\n--- LISTA COMPLETA DE COLUNAS ENCONTRADAS ---")
    # Imprime uma coluna por linha para facilitar a leitura no terminal
    for coluna in df_amostra.columns.tolist():
        print(coluna) 

except FileNotFoundError:
    print(f"\nERRO: Arquivo não encontrado em '{caminho_do_arquivo}'")
    print("Verifique se o seu arquivo CSV está mesmo dentro da pasta 'data' e se o nome está correto.")
except Exception as e:
    print(f"\nOcorreu um erro: {e}")