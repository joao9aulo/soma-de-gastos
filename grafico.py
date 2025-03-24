import pandas as pd
import os
import matplotlib.pyplot as plt

diretorio = '/media/joao9aulo/dados/Dropbox/Gasto meses/2024'

meses = []
gastos_supermercado = []

# Percorre todos os subdiretórios
for diretorio_atual, subdiretorios, arquivos in os.walk(diretorio):
    for arquivo in sorted(arquivos):  # Mantém a ordenação
        if arquivo.endswith('.ods'):
            caminho_completo = os.path.join(diretorio_atual, arquivo)
            
            # Ler arquivo
            df = pd.read_excel(caminho_completo, engine='odf', header=None)
            
            # Filtrar (mantido igual)
            mask = df[0].astype(str).str.strip().str.lower() == "relacionamentos"
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