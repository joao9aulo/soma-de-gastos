import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.stats import pearsonr, spearmanr


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

# Remover outliers das categorias específicas
categoria_saude = 'Saúde'
categoria_assinaturas = 'Assinaturas, Netflix/Serviços de Streaming/Assinaturas'

# Filtra valores <= 1500 para Saúde e Assinaturas
df_total[categoria_saude] = df_total[categoria_saude].where(df_total[categoria_saude] <= 1500)
df_total[categoria_assinaturas] = df_total[categoria_assinaturas].where(df_total[categoria_assinaturas] <= 1500)

# Calcular correlações com p-valores
print("\nCalculando correlações e p-valores...")
df_correlacoes = calcular_correlacoes_com_pvalor(df_total)
df_ordenado = df_correlacoes.sort_values(by='Correlação Absoluta', ascending=False)

# Opcional: Salvar resultados em CSV
df_ordenado.to_csv('correlacoes_categorias.csv', index=False)
print("\nArquivo 'correlacoes_categorias.csv' salvo com todas as correlações!")