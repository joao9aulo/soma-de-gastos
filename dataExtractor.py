import pandas as pd
import os

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
                    .isin(termos_formatados))
                
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

def get_combined_data(diretorio_base, categorias):
    """Retorna um DataFrame combinado com todos os dados coletados"""
    series_dados = []
    for cat in categorias:
        serie = coletar_dados(cat, diretorio_base)
        series_dados.append(serie)
    return pd.concat(series_dados, axis=1).dropna()
