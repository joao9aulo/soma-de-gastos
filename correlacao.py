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

def gerar_graficos_correlacao(df_correlacoes, df_dados, top_n=10, diretorio='graficos_correlacao'):
    """Gera gráficos de dispersão para os top N pares correlacionados"""
    if not os.path.exists(diretorio):
        os.makedirs(diretorio)
    
    top_pares = df_correlacoes.head(top_n)
    
    for index, row in top_pares.iterrows():
        cat_a = row['Categoria A']
        cat_b = row['Categoria B']
        pearson_r = row['Pearson (r)']
        pearson_p = row['Pearson (p)']
        spearman_rho = row['Spearman (ρ)']
        spearman_p = row['Spearman (p)']
        
        dados = df_dados[[cat_a, cat_b]].dropna()
        if len(dados) < 3:
            continue
        
        x = dados[cat_a]
        y = dados[cat_b]
        
        # Configurar o gráfico
        plt.figure(figsize=(10, 6))
        plt.scatter(x, y, alpha=0.5, label='Dados')
        
        # Adicionar linha de tendência
        coeficientes = np.polyfit(x, y, 1)
        linha_tendencia = np.polyval(coeficientes, x)
        plt.plot(x, linha_tendencia, color='red', linewidth=2, label='Linha de Tendência')
        
        # Configurações do gráfico
        plt.title(f'Correlação entre {cat_a} e {cat_b}', fontsize=14)
        plt.xlabel(cat_a, fontsize=12)
        plt.ylabel(cat_b, fontsize=12)
        plt.legend()
        
        # Adicionar texto com estatísticas
        texto_stats = (
            f'Pearson: r = {pearson_r:.2f} (p = {pearson_p:.3g})\n'
            f'Spearman: ρ = {spearman_rho:.2f} (p = {spearman_p:.3g})'
        )
        plt.gcf().text(0.5, 0.01, texto_stats, ha='center', fontsize=10, 
                      bbox=dict(facecolor='white', alpha=0.8))
        
        # Ajustar layout e salvar
        plt.tight_layout()
        nome_arquivo = f'correlacao_{cat_a}_vs_{cat_b}.png'.replace('/', '_').replace('\\', '_')
        caminho_completo = os.path.join(diretorio, nome_arquivo)
        plt.savefig(caminho_completo)
        plt.close()

# Obter dados e calcular correlações
df_total = get_combined_data()
print("\nCalculando correlações e p-valores...")
df_correlacoes = calcular_correlacoes_com_pvalor(df_total)
df_ordenado = df_correlacoes.sort_values(by='Correlação Absoluta', ascending=False)

# Salvar resultados em CSV
df_ordenado.to_csv('correlacoes_categorias.csv', index=False)
print("\nArquivo 'correlacoes_categorias.csv' salvo com todas as correlações!")

# Gerar gráficos para os top 10 pares
print("\nGerando gráficos das correlações...")
gerar_graficos_correlacao(df_ordenado, df_total, top_n=10)
print(f"Gráficos salvos no diretório 'graficos_correlacao'")