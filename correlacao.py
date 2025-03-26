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
    """Coleta dados para uma categoria específica"""
    meses = []
    gastos = []
    
    for diretorio_atual, subdiretorios, arquivos in os.walk(diretorio_base):
        subdiretorios[:] = ordenar_subdiretorios(subdiretorios)
        for arquivo in sorted(arquivos):
            if arquivo.endswith(('.ods', '.xlsx')):
                caminho_completo = os.path.join(diretorio_atual, arquivo)
                engine = 'odf' if arquivo.endswith('.ods') else 'openpyxl'
                
                df = pd.read_excel(caminho_completo, engine=engine, header=None)
                
                mask = df[0].astype(str).str.strip().str.lower() == categoria.lower()
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
    
    return pd.Series(gastos, index=meses, name=categoria)

def analisar_correlacao(cat1, cat2, diretorio_base):
    """
    Analisa a correlação entre duas categorias de gastos
    Retorna:
    - DataFrame com dados normalizados
    - Coeficientes de correlação
    - Gráficos comparativos
    """
    # Coleta dados
    dados1 = coletar_dados(cat1, diretorio_base)
    dados2 = coletar_dados(cat2, diretorio_base)
    
    # Cria DataFrame conjunto
    df = pd.DataFrame({cat1: dados1, cat2: dados2}).dropna()
    
    # Normaliza os dados para comparação visual
    df_normalizado = (df - df.min()) / (df.max() - df.min())
    
    # Calcula correlações
    pearson_r, pearson_p = pearsonr(df[cat1], df[cat2])
    spearman_r, spearman_p = spearmanr(df[cat1], df[cat2])
    
    # Cria figura
    plt.figure(figsize=(15, 10))
    
    # Gráfico 1: Sobreposição temporal
    plt.subplot(2, 1, 1)
    plt.plot(df_normalizado.index, df_normalizado[cat1], label=cat1, marker='o')
    plt.plot(df_normalizado.index, df_normalizado[cat2], label=cat2, marker='s')
    plt.title(f'Comparação Temporal: {cat1} vs {cat2}')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    
    # Gráfico 2: Dispersão com linha de tendência
    plt.subplot(2, 1, 2)
    plt.scatter(df[cat1], df[cat2], c='purple', alpha=0.7)
    
    # Linha de tendência
    z = np.polyfit(df[cat1], df[cat2], 1)
    p = np.poly1d(z)
    plt.plot(df[cat1], p(df[cat1]), "r--")
    
    plt.title(f'Correlação: Pearson r={pearson_r:.2f} (p={pearson_p:.3f})\nSpearman ρ={spearman_r:.2f} (p={spearman_p:.3f})')
    plt.xlabel(cat1)
    plt.ylabel(cat2)
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(f'correlacao_{cat1}_{cat2}.png', dpi=150)
    plt.close()
    
    return df, (pearson_r, pearson_p), (spearman_r, spearman_p)

# Exemplo de uso:
diretorio = '/media/joao9aulo/dados/Dropbox/Gasto meses/'
dados, pearson, spearman = analisar_correlacao('relacionamentos', 'transporte', diretorio)

print(f"Correlação de Pearson: {pearson[0]:.2f} (significância: {pearson[1]:.3f})")
print(f"Correlação de Spearman: {spearman[0]:.2f} (significância: {spearman[1]:.3f})")