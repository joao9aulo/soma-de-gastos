import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.stats import pearsonr, spearmanr

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

def coletar_dados(categoria, diretorio_base):
    """Coleta dados para uma categoria com múltiplas strings possíveis"""
    meses = []
    gastos = []
    
    termos = [categoria] if isinstance(categoria, str) else categoria
    nome_categoria = ', '.join(termos) if isinstance(categoria, list) else categoria
    
    for diretorio_atual, subdiretorios, arquivos in os.walk(diretorio_base):
        subdiretorios[:] = ordenar_subdiretorios(subdiretorios)
        for arquivo in sorted(arquivos):
            if arquivo.endswith(('.ods', '.xlsx')):
                caminho_completo = os.path.join(diretorio_atual, arquivo)
                engine = 'odf' if arquivo.endswith('.ods') else 'openpyxl'
                
                df = pd.read_excel(caminho_completo, engine=engine, header=None)
                
                termos_formatados = [str(t).strip().lower() for t in termos]
                mask = (
                    df[0]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .isin(termos_formatados)
                )
                
                df_filtrado = df.loc[mask].copy()
                
                if not df_filtrado.empty:
                    valores = (
                        df_filtrado.loc[:, 1]
                        .astype(str)
                        .str.replace(r'R\$|\s+', '', regex=True)
                        .str.replace('.00', '')
                        .str.replace(',', '.')
                        .pipe(pd.to_numeric, errors='coerce'))
                    soma = valores.abs().sum()
                else:
                    soma = 0
                
                mes = os.path.relpath(caminho_completo, start=diretorio_base).replace('.ods', '')
                meses.append(mes)
                gastos.append(soma)
    
    return pd.Series(gastos, index=meses, name=nome_categoria)

# Configurações iniciais
diretorio = '/media/joao9aulo/dados/Dropbox/Gasto meses/'

# Definir todas as categorias para análise
categorias = [
    ['relacionamentos', 'GP', 'civis'],
    ['transporte','Uber/Táxi','ônibus'],
    ['Rolês/Saídas','Shows/Eventos','Restaurantes/Bares'],
    ##['aporte'],
    ['celular'],
    ['supermercado'],
    ['aluguel'],
    ['luz'],
    ['Assinaturas','Netflix/Serviços de Streaming/Assinaturas'],
    ['Saúde'],
    ['Ifood/Semelhantes','Lanches/Almoço extra'],
    ['Cinema'],
    ['Internet'],
    ['Aparência'],
    ['Gás'],
    ['Doações/Presentes'],
    ['Utilidades'],
    ['Livros'],
    ['HQ'],
    ['Bugigangas'],
    ['Games']


]

# Coletar dados para todas as categorias
print("Coletando dados de todas as categorias...")
series_dados = []
for cat in categorias:
    serie = coletar_dados(cat, diretorio)
    series_dados.append(serie)
    print(f"Dados coletados para: {serie.name}")

# Criar DataFrame combinado
df_total = pd.concat(series_dados, axis=1).dropna()

# Calcular matrizes de correlação
print("\nCalculando correlações...")
corr_pearson = df_total.corr(method='pearson')
corr_spearman = df_total.corr(method='spearman')

# Extrair e ordenar pares de correlação
pares = []
n_categorias = len(df_total.columns)
for i in range(n_categorias):
    for j in range(i+1, n_categorias):
        cat1 = df_total.columns[i]
        cat2 = df_total.columns[j]
        
        pares.append({
            'Categoria A': cat1,
            'Categoria B': cat2,
            'Pearson': corr_pearson.iloc[i, j],
            'Spearman': corr_spearman.iloc[i, j],
            'Correlação Absoluta': abs(corr_pearson.iloc[i, j])
        })

# Criar e ordenar DataFrame
df_correlacoes = pd.DataFrame(pares)
df_ordenado = df_correlacoes.sort_values(by='Correlação Absoluta', ascending=False)

# Exibir resultados
print("\nTop 10 correlações mais fortes:")
print(df_ordenado[['Categoria A', 'Categoria B', 'Pearson', 'Spearman']].head(30))

# Opcional: Salvar resultados em CSV
df_ordenado.to_csv('correlacoes_categorias.csv', index=False)
print("\nArquivo 'correlacoes_categorias.csv' salvo com todas as correlações!")

# Opcional: Plotar matriz de correlação
plt.figure(figsize=(12, 8))
plt.matshow(corr_pearson, fignum=1, cmap='coolwarm')
plt.xticks(range(len(df_total.columns)), df_total.columns, rotation=90)
plt.yticks(range(len(df_total.columns)), df_total.columns)
plt.colorbar()
plt.title('Matriz de Correlação de Pearson')
plt.tight_layout()
plt.savefig('matriz_correlacao.png', dpi=150)
print("Matriz de correlação salva como 'matriz_correlacao.png'")