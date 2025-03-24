import pandas as pd
import os

diretorio = '/media/joao9aulo/dados/Dropbox/Gasto meses/'
total_geral = 0.0
contador_arquivos = 0

for arquivo in os.listdir(diretorio):
    if arquivo.endswith('.ods'):
        caminho_completo = os.path.join(diretorio, arquivo)
        
        # Ler o arquivo ODS
        df = pd.read_excel(caminho_completo, engine='odf', header=None)
        
        # Filtrar linhas onde a coluna 0 NÃO é "aporte" (ajuste o índice conforme necessário)
        # Convertemos para string e aplicamos strip() para evitar problemas com espaços
        df = df[df[0].astype(str).str.strip().str.lower() != "aporte"]
        
        # Processar a coluna de valores (coluna 1)
        df[1] = df[1].astype(str)
        df[1] = df[1].str.replace('R$ ', '', regex=True).str.strip()
        df[1] = df[1].str.replace('.00', '').str.replace(',', '.')
        
        # Converter para números e somar
        valores = pd.to_numeric(df[1], errors='coerce')
        
        if valores.isna().any():
            print(f"Valores inválidos em {arquivo} (ignorados)")
        
        soma_arquivo = valores.sum()
        print(f"Soma de {arquivo}: R$ {soma_arquivo:.2f}")
        total_geral += soma_arquivo
        contador_arquivos += 1

if contador_arquivos == 0:
    print("Nenhum arquivo .ods encontrado!")
else:
    # Formatar valores
    total_formatado = f"R$ {total_geral:,.2f}".replace(',', 'temp').replace('.', ',').replace('temp', '.')
    media = total_geral / contador_arquivos
    media_formatada = f"R$ {media:,.2f}".replace(',', 'temp').replace('.', ',').replace('temp', '.')

    print(f"\nTotal geral (aporte excluído): {total_formatado}")
    print(f"Média por arquivo: {media_formatada}")