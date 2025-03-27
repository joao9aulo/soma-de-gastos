import pandas as pd
import os
import matplotlib.pyplot as plt

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

def coletar_dados_agregados(categorias_agregadas, diretorio_base):
    """Coleta dados agregados para múltiplas categorias"""
    dados = {categoria: [] for categoria in categorias_agregadas.keys()}
    meses = []
    
    for diretorio_atual, subdiretorios, arquivos in os.walk(diretorio_base):
        subdiretorios[:] = ordenar_subdiretorios(subdiretorios)
        for arquivo in sorted(arquivos):
            if arquivo.endswith(('.ods', '.xlsx')):
                caminho_completo = os.path.join(diretorio_atual, arquivo)
                engine = 'odf' if arquivo.endswith('.ods') else 'openpyxl'
                
                df = pd.read_excel(caminho_completo, engine=engine, header=None)
                df[0] = df[0].astype(str).str.strip().str.lower()
                
                # Coleta soma para cada categoria
                soma_por_categoria = {}
                for categoria, padroes in categorias_agregadas.items():
                    mask = df[0].isin([p.strip().lower() for p in padroes])
                    df_filtrado = df.loc[mask].copy()
                    if not df_filtrado.empty:
                        valores = (
                            df_filtrado[1]
                            .astype(str)
                            .str.replace(r'R\$|\s+', '', regex=True)
                            .str.replace('.00', '')
                            .str.replace(',', '.')
                            .pipe(pd.to_numeric, errors='coerce')
                            .abs()
                        )
                        soma_por_categoria[categoria] = valores.sum()
                    else:
                        soma_por_categoria[categoria] = 0
                
                # Adiciona aos dados
                for categoria in categorias_agregadas.keys():
                    dados[categoria].append(soma_por_categoria.get(categoria, 0))
                
                mes = os.path.relpath(caminho_completo, start=diretorio_base)
                mes = mes.replace('.ods', '').replace('.xlsx', '')
                meses.append(mes)
    
    return dados, meses

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
    dados_x, meses = coletar_dados_agregados(categoria_x, diretorio_base)
    dados_y, _ = coletar_dados_agregados(categoria_y, diretorio_base)
    
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