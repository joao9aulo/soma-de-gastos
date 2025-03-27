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

def gerar_grafico_com_agregacao(categorias_agregadas, diretorio_base=None, cores=None):
    """
    Gera gráfico de evolução de gastos com categorias agregadas
    
    Parâmetros:
    categorias_agregadas (dict): Dicionário no formato {NomeCategoria: [padrões]}
    diretorio_base (str): Caminho base dos arquivos (opcional)
    cores (list): Lista de cores para cada categoria (opcional)
    """
    if diretorio_base is None:
        diretorio_base = '/media/joao9aulo/dados/Dropbox/Gasto meses/'

    # Configura cores
    nomes_categorias = list(categorias_agregadas.keys())
    if cores is None:
        cores = plt.rcParams['axes.prop_cycle'].by_key()['color'][:len(nomes_categorias)]
    elif len(cores) != len(nomes_categorias):
        raise ValueError("Número de cores deve ser igual ao número de categorias")

    meses = []
    gastos_por_categoria = {categoria: [] for categoria in nomes_categorias}

    for diretorio_atual, subdiretorios, arquivos in os.walk(diretorio_base):
        subdiretorios[:] = ordenar_subdiretorios(subdiretorios)
        for arquivo in sorted(arquivos):
            if arquivo.endswith(('.ods', '.xlsx')):
                caminho_completo = os.path.join(diretorio_atual, arquivo)
                engine = 'odf' if arquivo.endswith('.ods') else 'openpyxl'
                
                df = pd.read_excel(caminho_completo, engine=engine, header=None)
                df[0] = df[0].astype(str).str.strip().str.lower()  # Normaliza

                # Calcula soma para cada categoria agregada
                soma_por_categoria = {categoria: 0 for categoria in nomes_categorias}
                
                for categoria, padroes in categorias_agregadas.items():
                    # Cria máscara combinando todos os padrões
                    mask = df[0].isin([p.strip().lower() for p in padroes])
                    
                    # Filtra e processa valores
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
                
                mes = os.path.relpath(caminho_completo, start=diretorio_base)
                mes = mes.replace('.ods', '').replace('.xlsx', '')
                meses.append(mes)
                
                for categoria in nomes_categorias:
                    gastos_por_categoria[categoria].append(soma_por_categoria[categoria])

    # Geração do gráfico
    plt.figure(figsize=(36, 6))
    for categoria, cor in zip(nomes_categorias, cores):
        plt.plot(meses, gastos_por_categoria[categoria], 
                marker='o', linestyle='-', color=cor, label=categoria)
    
    plt.title('Evolução dos Gastos com Categorias Agregadas (2024)')
    plt.xlabel('Local/Mês')
    plt.ylabel('Valor Gasto (R$)')
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()

    # Formatação monetária
    plt.gca().yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f'R$ {x:,.2f}'.replace(',', 'temp').replace('.', ',').replace('temp', '.'))
    )

    nome_arquivo = 'gastos_agregados_' + '_'.join(nomes_categorias).lower().replace(' ', '_') + '.png'
    plt.savefig(nome_arquivo, dpi=300)
    plt.close()
    print(f"Gráfico salvo como {nome_arquivo}")

# Exemplo de uso:
gerar_grafico_com_agregacao(
    categorias_agregadas={
        'Assinaturas': [
            'Assinaturas',
            'Netflix/Serviços de Streaming/Assinaturas'
        ]
    },
    cores=['purple']
)

gerar_grafico_com_agregacao(
    categorias_agregadas={
        'Rolês': [
            'Rolês/Saídas', 'Shows/Eventos','Restaurantes/Bares'
        ]
    },
    cores=['purple']
)

gerar_grafico_com_agregacao(
    categorias_agregadas={
        'transporte': [
            'transporte','Uber/Táxi','ônibus'
        ]
    },
    cores=['purple']
)

gerar_grafico_com_agregacao(
    categorias_agregadas={
        'celular': [
            'celular'
        ]
    },
    cores=['purple']
)

gerar_grafico_com_agregacao(
    categorias_agregadas={
        'aluguel': [
            'aluguel'
        ]
    },
    cores=['purple']
)