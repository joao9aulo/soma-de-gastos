import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.stats import pearsonr, spearmanr

def ordenar_subdiretorios(subdiretorios):
    """Ordena subdiretórios numericamente, ignorando não numéricos"""
    ordenados = []
    for dir in subdiretorios:
        try:
            ordenados.append((int(dir), dir))
        except ValueError:
            ordenados.append((float('inf'), dir))
    ordenados.sort(key=lambda x: x[0])
    return [dir for (_, dir) in ordenados]

def coletar_dados(categoria, diretorio_base):
    """Coleta dados para uma categoria com múltiplas strings possíveis"""
    meses = []
    gastos = []
    
    # Converter para lista se for string único
    termos = [categoria] if isinstance(categoria, str) else categoria
    nome_categoria = ', '.join(termos) if isinstance(categoria, list) else categoria
    
    for diretorio_atual, subdiretorios, arquivos in os.walk(diretorio_base):
        subdiretorios[:] = ordenar_subdiretorios(subdiretorios)
        for arquivo in sorted(arquivos):
            if arquivo.endswith(('.ods', '.xlsx')):
                caminho_completo = os.path.join(diretorio_atual, arquivo)
                engine = 'odf' if arquivo.endswith('.ods') else 'openpyxl'
                
                df = pd.read_excel(caminho_completo, engine=engine, header=None)
                
                # Criar máscara para qualquer um dos termos
                termos_formatados = [str(t).strip().lower() for t in termos]
                mask = (
                    df[0]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .isin(termos_formatados)
                )
                
                df_filtrado = df.loc[mask].copy()
                
                if not df_filtrado.empty:
                    valores = (
                        df_filtrado.loc[:, 1]
                        .astype(str)
                        .str.replace(r'R\$|\s+', '', regex=True)
                        .str.replace('.00', '')
                        .str.replace(',', '.')
                        .pipe(pd.to_numeric, errors='coerce')
                    )
                    soma = valores.abs().sum()
                else:
                    soma = 0
                
                mes = os.path.relpath(caminho_completo, start=diretorio_base).replace('.ods', '')
                meses.append(mes)
                gastos.append(soma)
    
    return pd.Series(gastos, index=meses, name=nome_categoria)

def analisar_correlacao(cat1, cat2, diretorio_base):
    """
    Analisa a correlação entre duas categorias (podem ser listas de termos)
    Retorna:
    - DataFrame com dados normalizados
    - Coeficientes de correlação
    - Gráficos comparativos
    """
    # Coleta dados
    dados1 = coletar_dados(cat1, diretorio_base)
    dados2 = coletar_dados(cat2, diretorio_base)
    
    # Cria DataFrame conjunto
    df = pd.DataFrame({dados1.name: dados1, dados2.name: dados2}).dropna()
    
    # Normalização
    df_normalizado = (df - df.min()) / (df.max() - df.min())
    
    # Cálculo de correlações
    pearson_r, pearson_p = pearsonr(df[dados1.name], df[dados2.name])
    spearman_r, spearman_p = spearmanr(df[dados1.name], df[dados2.name])
    
    # Plot
    plt.figure(figsize=(15, 10))
    
    # Gráfico 1: Sobreposição temporal
    plt.subplot(2, 1, 1)
    plt.plot(df_normalizado.index, df_normalizado[dados1.name], label=dados1.name, marker='o')
    plt.plot(df_normalizado.index, df_normalizado[dados2.name], label=dados2.name, marker='s')
    plt.title(f'Comparação Temporal: {dados1.name} vs {dados2.name}')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    
    # Gráfico 2: Dispersão
    plt.subplot(2, 1, 2)
    plt.scatter(df[dados1.name], df[dados2.name], c='purple', alpha=0.7)
    
    # Linha de tendência
    z = np.polyfit(df[dados1.name], df[dados2.name], 1)
    p = np.poly1d(z)
    plt.plot(df[dados1.name], p(df[dados1.name]), "r--")
    
    plt.title(f'Correlação: Pearson r={pearson_r:.2f} (p={pearson_p:.3f})\nSpearman ρ={spearman_r:.2f} (p={spearman_p:.3f})')
    plt.xlabel(dados1.name)
    plt.ylabel(dados2.name)
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(f'correlacao_{dados1.name}_{dados2.name}.png', dpi=150)
    plt.close()
    
    return df, (pearson_r, pearson_p), (spearman_r, spearman_p)

# Exemplo de uso com múltiplos termos:
diretorio = '/media/joao9aulo/dados/Dropbox/Gasto meses/'

# Categorias com múltiplos termos
relacionamentos = ['relacionamentos', 'GP', 'civis']
transporte = ['transporte','Uber/Táxi']

dados, pearson, spearman = analisar_correlacao(relacionamentos, transporte, diretorio)

print(f"Correlação de Pearson: {pearson[0]:.2f} (significância: {pearson[1]:.3f})")
print(f"Correlação de Spearman: {spearman[0]:.2f} (significância: {spearman[1]:.3f})")