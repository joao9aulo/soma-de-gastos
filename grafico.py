import pandas as pd
import os
import matplotlib.pyplot as plt

diretorio = '/media/joao9aulo/dados/Dropbox/Gasto meses/2024'

# Listas para armazenar dados do gráfico
meses = []
gastos_supermercado = []

for arquivo in sorted(os.listdir(diretorio)):
    if arquivo.endswith('.ods'):
        caminho_completo = os.path.join(diretorio, arquivo)
        
        # Ler arquivo
        df = pd.read_excel(caminho_completo, engine='odf', header=None)
        
        # Filtrar usando .loc para manter a referência original
        mask = df[0].astype(str).str.strip().str.lower() == "relacionamentos"
        df_supermercado = df.loc[mask].copy()
        
        if not df_supermercado.empty:
            # Processar valores diretamente para numérico
            valores = (
                df_supermercado.loc[:, 1]
                .astype(str)
                .str.replace(r'R\$|\s+', '', regex=True)  # Remove R$ e espaços
                .str.replace('.00', '')
                .str.replace(',', '.')
                .pipe(pd.to_numeric, errors='coerce')
            )
            
            # Atribuir valores numéricos de volta ao DataFrame
            df_supermercado.loc[:, 1] = valores
            soma = df_supermercado[1].sum()
        else:
            soma = 0
        
        # Adicionar às listas
        meses.append(os.path.splitext(arquivo)[0])
        gastos_supermercado.append(soma)

# Configuração do gráfico
plt.figure(figsize=(12, 6))
plt.plot(meses, gastos_supermercado, marker='o', linestyle='-', color='green')
plt.title('Evolução dos Gastos com Supermercado (2024)')
plt.xlabel('Mês')
plt.ylabel('Valor Gasto (R$)')
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()

# Formatação monetária correta
plt.gca().yaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, _: f'R$ {x:,.2f}'.replace(',', 'temp').replace('.', ',').replace('temp', '.'))
)

plt.savefig('gastos_supermercado.png')
print("Gráfico salvo como gastos_supermercado.png")