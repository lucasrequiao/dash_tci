import pandas as pd  # pyright: ignore[reportMissingImports]
import streamlit as st   # pyright: ignore[reportMissingImports]
from leitor import carregar_dados

st.set_page_config(page_title="Painel de TCIs", page_icon=":bar_chart:", layout="wide")
st.title("Painel de TCIs")

df = carregar_dados()

total_tcis = len(df)
estabelecimentos_unicos = df["chave_estabelecimento"].nunique()
reincidentes = (df["chave_estabelecimento"].value_counts() > 1).sum()
pct_validados = df["Status"].eq("VALIDADO").mean() * 100
cidades = df["Cidade"].nunique()

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("Total de TCIs", total_tcis)
with c2:
    st.metric("Estabelecimentos únicos", estabelecimentos_unicos)
with c3:
    st.metric("Reincidentes (>1 TCI)", reincidentes)
with c4:
    st.metric("Validados", f"{pct_validados:.0f}%")
with c5:
    st.metric("Cidades", cidades)

st.divider()

st.dataframe(df, width="stretch", hide_index=True)