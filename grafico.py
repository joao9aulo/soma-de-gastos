import pandas as pd
import os
import matplotlib.pyplot as plt

def ordenar_subdiretorios(subdiretorios):
    """Ordena subdiretórios numericamente, ignorando não numéricos"""
    ordenados = []
    for dir in subdiretorios:
        try:
            # Tenta converter para inteiro (para ordenação numérica)
            ordenados.append((int(dir), dir))
        except ValueError:
            # Mantém diretórios não numéricos no final
            ordenados.append((float('inf'), dir))
    
    # Ordena primeiro pelos números, depois pelos não numéricos
    ordenados.sort(key=lambda x: x[0])
    return [dir for (_, dir) in ordenados]

diretorio = '/media/joao9aulo/dados/Dropbox/Gasto meses/'

meses = []
gastos_supermercado = []

# Percorre todos os subdiretórios
for diretorio_atual, subdiretorios, arquivos in os.walk(diretorio):
    subdiretorios[:] = ordenar_subdiretorios(subdiretorios)
    for arquivo in sorted(arquivos):  # Mantém a ordenação
        if arquivo.endswith(('.ods', '.xlsx')):
            caminho_completo = os.path.join(diretorio_atual, arquivo)

             # Determina o engine pelo tipo de arquivo
            engine = 'odf' if arquivo.endswith('.ods') else 'openpyxl'
            
            # Ler arquivo
            df = pd.read_excel(caminho_completo, engine=engine, header=None)
            
            # Filtrar (mantido igual)
            mask = (
            (df[0].astype(str).str.strip().str.lower() == "relacionamentos") |
            (df[0].astype(str).str.strip().str.lower() == "gp"))
            df_supermercado = df.loc[mask].copy()
            
            if not df_supermercado.empty:
                # Processamento numérico (mantido igual)
                valores = (
                    df_supermercado.loc[:, 1]
                    .astype(str)
                    .str.replace(r'R\$|\s+', '', regex=True)
                    .str.replace('.00', '')
                    .str.replace(',', '.')
                    .pipe(pd.to_numeric, errors='coerce')
                )
                df_supermercado.loc[:, 1] = valores
                soma = df_supermercado[1].sum()
            else:
                soma = 0
            
            # Adiciona o caminho relativo para identificar meses
            mes = os.path.relpath(caminho_completo, start=diretorio).replace('.ods', '')
            meses.append(mes)
            gastos_supermercado.append(soma)

# Restante do código mantido igual...
plt.figure(figsize=(12, 6))
plt.plot(meses, gastos_supermercado, marker='o', linestyle='-', color='green')
plt.title('Evolução dos Gastos com Supermercado (2024)')
plt.xlabel('Local/Mês')
plt.ylabel('Valor Gasto (R$)')
plt.xticks(rotation=45, ha='right')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()

# Formatação monetária
plt.gca().yaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, _: f'R$ {x:,.2f}'.replace(',', 'temp').replace('.', ',').replace('temp', '.'))
)

plt.savefig('gastos_supermercado.png', dpi=300)
print("Gráfico salvo como gastos_supermercado.png")