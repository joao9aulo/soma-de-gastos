import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.stats import pearsonr, spearmanr
from dataExtractor import get_combined_data
import matplotlib.dates as mdates  # Adicionar este import

def gerar_graficos_crescimento(df, diretorio='graficos_crescimento'):
    """Gera gráficos de crescimento ao longo do tempo para cada categoria"""
    if not os.path.exists(diretorio):
        os.makedirs(diretorio)
    
    for categoria in df.columns:
        dados = df[[categoria]].dropna()
        if len(dados) < 1:
            print(f"Não há dados suficientes para {categoria}")
            continue
        
        plt.figure(figsize=(40, 6))
        plt.plot(dados.index, dados[categoria], marker='o', linestyle='-', markersize=4, label=categoria)
        plt.title(f'Crescimento de {categoria} ao longo do tempo', fontsize=14)
        plt.xlabel('Ano', fontsize=12)  # Alterado de 'Data' para 'Ano'
        plt.ylabel('Valor', fontsize=12)
        plt.grid(True)
        plt.legend()
        
        # Configurar formatação do eixo x para mostrar anos
        ax = plt.gca()
        
        # Verificar se o índice é datetime
        if isinstance(dados.index, pd.DatetimeIndex):
            # Calcular intervalo de anos dinamicamente
            start_year = dados.index.min().year
            end_year = dados.index.max().year
            num_years = end_year - start_year + 1
            
            # Definir intervalo de exibição
            if num_years > 20:
                intervalo = 5
            elif num_years > 10:
                intervalo = 2
            else:
                intervalo = 1
            
            # Aplicar formatação
            ax.xaxis.set_major_locator(mdates.YearLocator(intervalo))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            
            # Rotacionar labels para melhor legibilidade
            plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        nome_arquivo = f'crescimento_{categoria}.png'.replace('/', '_').replace('\\', '_')
        caminho_completo = os.path.join(diretorio, nome_arquivo)
        plt.savefig(caminho_completo)
        plt.close()
        
# Obter dados e calcular correlações
df_total = get_combined_data()

# Verificar e configurar índice de tempo
if not isinstance(df_total.index, pd.DatetimeIndex):
    if 'Data' in df_total.columns:
        try:
            df_total['Data'] = pd.to_datetime(df_total['Data'])
            df_total.set_index('Data', inplace=True)
            print("\nColuna 'Data' definida como índice datetime.")
        except Exception as e:
            print(f"\nErro ao converter 'Data': {str(e)}")
    else:
        print("\nAviso: Índice não é datetime. Gráficos usarão o índice atual.")

# ... (código existente para correlações e gráficos de dispersão)

# Gerar gráficos de crescimento
print("\nGerando gráficos de crescimento ao longo do tempo...")
gerar_graficos_crescimento(df_total)
print(f"Gráficos de crescimento salvos no diretório 'graficos_crescimento'")