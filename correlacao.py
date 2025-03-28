import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.stats import pearsonr, spearmanr
from dataExtractor import get_combined_data

def calcular_correlacoes_com_pvalor(df):
    """Calcula correlações e p-valores para todos os pares de categorias"""
    pares = []
    categorias = df.columns.tolist()
    
    for i in range(len(categorias)):
        for j in range(i+1, len(categorias)):
            cat1 = categorias[i]
            cat2 = categorias[j]
            
            # Remove NaN para o par atual
            dados = df[[cat1, cat2]].dropna()
            
            if len(dados) < 3:
                continue  # Mínimo de 3 pontos para correlação
                
            try:
                # Pearson
                pearson_corr, pearson_p = pearsonr(dados[cat1], dados[cat2])
                
                # Spearman
                spearman_corr, spearman_p = spearmanr(dados[cat1], dados[cat2])
                
                pares.append({
                    'Categoria A': cat1,
                    'Categoria B': cat2,
                    'Pearson (r)': pearson_corr,
                    'Pearson (p)': pearson_p,
                    'Spearman (ρ)': spearman_corr,
                    'Spearman (p)': spearman_p,
                    'Correlação Absoluta': abs(pearson_corr)
                })
                
            except Exception as e:
                print(f"Erro em {cat1} vs {cat2}: {str(e)}")
    
    return pd.DataFrame(pares)

df_total = get_combined_data()

# Calcular correlações com p-valores
print("\nCalculando correlações e p-valores...")
df_correlacoes = calcular_correlacoes_com_pvalor(df_total)
df_ordenado = df_correlacoes.sort_values(by='Correlação Absoluta', ascending=False)

# Opcional: Salvar resultados em CSV
df_ordenado.to_csv('correlacoes_categorias.csv', index=False)
print("\nArquivo 'correlacoes_categorias.csv' salvo com todas as correlações!")