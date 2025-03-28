import pandas as pd
import os
import matplotlib.pyplot as plt
from dataExtractor import get_combined_data

def gerar_grafico_com_agregacao(categorias_agregadas, diretorio_base=None, cores=None):
    """Gera gráfico de linha ou dispersão para uma categoria (como antes)"""
    # ... (mantenha o código original desta função) ...

def gerar_grafico_dispersao(categoria_x, categoria_y, diretorio_base=None, cor='blue'):
    """
    Gera gráfico de dispersão comparando duas categorias de gastos.
    
    Parâmetros:
    categoria_x (dict): Categoria para eixo X (ex: {'Rolês': [...]}).
    categoria_y (dict): Categoria para eixo Y (ex: {'Transporte': [...]}).
    diretorio_base (str): Caminho base dos arquivos.
    cor (str): Cor dos pontos no gráfico.
    """
    if diretorio_base is None:
        diretorio_base = '/media/joao9aulo/dados/Dropbox/Gasto meses/'
    
    # Coleta dados para ambas as categorias
    dados_x, meses = get_combined_data()
    dados_y, _ = get_combined_data()
    
    nome_x = list(categoria_x.keys())[0]
    nome_y = list(categoria_y.keys())[0]
    valores_x = dados_x[nome_x]
    valores_y = dados_y[nome_y]
    
    # Geração do gráfico de dispersão
    plt.figure(figsize=(10, 6))
    plt.scatter(valores_x, valores_y, color=cor, alpha=0.7, edgecolors='w')
    
    plt.title(f'Relação entre {nome_x} vs {nome_y}')
    plt.xlabel(f'Gastos com {nome_x} (R$)')
    plt.ylabel(f'Gastos com {nome_y} (R$)')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Formatação monetária
    plt.gca().xaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f'R$ {x:,.2f}'.replace(',', 'temp').replace('.', ',').replace('temp', '.'))
    )
    plt.gca().yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f'R$ {x:,.2f}'.replace(',', 'temp').replace('.', ',').replace('temp', '.'))
    )
    
    # Adiciona rótulos dos meses aos pontos
    for i, mes in enumerate(meses):
        plt.annotate(mes, (valores_x[i], valores_y[i]), fontsize=8, alpha=0.7)
    
    plt.tight_layout()
    nome_arquivo = f'dispersao_{nome_x}_vs_{nome_y}.png'
    plt.savefig(nome_arquivo, dpi=300)
    plt.close()
    print(f"Gráfico de dispersão salvo como {nome_arquivo}")

# Exemplo de uso:
gerar_grafico_dispersao(
    categoria_x={'saúde': ['saúde']},
    categoria_y={'Rolês': ['Rolês/Saídas','Shows/Eventos','Restaurantes/Bares']},
    cor='green'
)

# Exemplo de uso:
gerar_grafico_dispersao(
    categoria_x={'saúde': ['saúde']},
    categoria_y={'Transporte': ['transporte']},
    cor='green'
)