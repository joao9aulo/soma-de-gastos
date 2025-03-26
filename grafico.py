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

def gerar_grafico(categoria, diretorio_base=None, cor='green'):
    """
    Gera gráfico de evolução de gastos para uma categoria específica
    
    Parâmetros:
    categoria (str): Nome da categoria de gastos a ser filtrada
    diretorio_base (str): Caminho base dos arquivos (opcional)
    cor (str): Cor do gráfico (opcional)
    """
    if diretorio_base is None:
        diretorio_base = '/media/joao9aulo/dados/Dropbox/Gasto meses/'

    meses = []
    gastos = []

    for diretorio_atual, subdiretorios, arquivos in os.walk(diretorio_base):
        subdiretorios[:] = ordenar_subdiretorios(subdiretorios)
        for arquivo in sorted(arquivos):
            if arquivo.endswith(('.ods', '.xlsx')):
                caminho_completo = os.path.join(diretorio_atual, arquivo)
                engine = 'odf' if arquivo.endswith('.ods') else 'openpyxl'
                
                df = pd.read_excel(caminho_completo, engine=engine, header=None)
                
                # Filtra pela categoria (case insensitive)
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
                    df_filtrado.loc[:, 1] = valores
                    soma = df_filtrado[1].abs().sum()
                else:
                    soma = 0
                
                mes = os.path.relpath(caminho_completo, start=diretorio_base).replace('.ods', '')
                meses.append(mes)
                gastos.append(soma)

    # Geração do gráfico
    plt.figure(figsize=(36, 6))
    plt.plot(meses, gastos, marker='o', linestyle='-', color=cor)
    plt.title(f'Evolução dos Gastos com {categoria.capitalize()} (2024)')
    plt.xlabel('Local/Mês')
    plt.ylabel('Valor Gasto (R$)')
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Formatação monetária
    plt.gca().yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f'R$ {x:,.2f}'.replace(',', 'temp').replace('.', ',').replace('temp', '.'))
    )

    nome_arquivo = f'gastos_{categoria.lower().replace(" ", "_")}.png'
    plt.savefig(nome_arquivo, dpi=300)
    plt.close()  # Fecha a figura para liberar memória
    print(f"Gráfico salvo como {nome_arquivo}")

# Exemplo de uso:
gerar_grafico('transporte', cor='blue')
gerar_grafico('supermercado')
