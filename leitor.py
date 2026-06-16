from pathlib import Path
import pandas as pd  # pyright: ignore[reportMissingImports]
import streamlit as st
from limpeza import limpar

PASTA_DADOS = Path(__file__).resolve().parent / "data"

@st.cache_data
def carregar_dados() -> pd.DataFrame:
    # 1. Varre a pasta data/ e lê TODOS os .csv encontrados
    arquivos = sorted(PASTA_DADOS.glob("*.csv"))

    if not arquivos:
        raise FileNotFoundError(f"Não foi encontrado nenhum arquivo CSV na pasta {PASTA_DADOS}")

    quadros = []
    for arquivo in arquivos:
        bruto = pd.read_csv(arquivo, dtype={"CPF/CNPJ": str})
        bruto["_origem"] = arquivo.name
        quadros.append(bruto) 

    df = pd.concat(quadros, ignore_index=True) 

    # 2. Deduplica pela chave única `id` (mantém a última ocorrência)
    antes = len(df)
    df = df.drop_duplicates(subset="id", keep="last").reset_index(drop=True)
    df.attrs["duplicatas_removidas"] = antes - len(df)

    return limpar(df)

