import pandas as pd  # pyright: ignore[reportMissingImports]
import streamlit as st   # pyright: ignore[reportMissingImports]
from leitor import carregar_dados

st.set_page_config(page_title="Painel de TCIs", page_icon=":bar_chart:", layout="wide")
st.title("Painel de TCIs")

df = carregar_dados()

st.sidebar.header("Filtros")

data_min = df["dataCadastro"].min().date()
data_max = df["dataCadastro"].max().date()
periodo = st.sidebar.date_input("Período", value=(data_min, data_max), min_value=data_min, max_value=data_max)
status_selecionado = st.sidebar.multiselect("Status", sorted(df["Status"].unique()), default=list(df["Status"].unique()))
cidade_selecionada = st.sidebar.multiselect("Cidade", sorted(df["Cidade"].unique()))
bpm_selecionado = st.sidebar.multiselect("Batalhão", sorted(df["Batalhão"].unique()))
infracao_selecionada = st.sidebar.multiselect("Tipo de Infração", sorted(df["infracaoObservada"].unique()))

df_filtrado = df.copy()

if isinstance(periodo, (tuple, list)) and len(periodo) == 2:
    ini, fim = periodo
    df_filtrado = df_filtrado[(df_filtrado["dataCadastro"].dt.date >= ini) & (df_filtrado["dataCadastro"].dt.date <= fim)]
if status_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Status"].isin(status_selecionado)]
if cidade_selecionada:
    df_filtrado = df_filtrado[df_filtrado["Cidade"].isin(cidade_selecionada)]
if bpm_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Batalhão"].isin(bpm_selecionado)]
if infracao_selecionada:
    df_filtrado = df_filtrado[df_filtrado["infracaoObservada"].isin(infracao_selecionada)]
if df_filtrado.empty:
    st.warning("Nenhum TCI corresponde aos filtros selecionados")
    st.stop()

total_tcis = len(df_filtrado)
estabelecimentos_unicos = df_filtrado["chave_estabelecimento"].nunique()
reincidentes = (df_filtrado["chave_estabelecimento"].value_counts() > 1).sum()
pct_validados = df_filtrado["Status"].eq("VALIDADO").mean() * 100
cidades = df_filtrado["Cidade"].nunique()

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

st.dataframe(df_filtrado, width="stretch", hide_index=True)