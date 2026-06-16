import pandas as pd  # pyright: ignore[reportMissingImports]
import streamlit as st   # pyright: ignore[reportMissingImports]
import plotly.express as px
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

# ===================== MAPA =====================
st.subheader("Distribuição geográfica dos TCIs")
mapa_df = df_filtrado[df_filtrado["coord_valida"]]

fig_mapa = px.scatter_map(
    mapa_df,
    lat="LAT",
    lon="LONG",
    color="Status",
    hover_name="Distribuidora",
    hover_data={"Cidade": True, "Endereço": True, "Batalhão": True, "infracaoObservada": True, "LAT": False, "LONG": False},
    zoom=9.2,
    height=520
)
fig_mapa.update_traces(marker=dict(size=8, opacity=0.75))
fig_mapa.update_layout(
    map_style="carto-positron", #"open-street-map"
    margin=dict(l=0, r=0, t=0, b=0)
)
st.plotly_chart(fig_mapa, width="stretch")

# ===================== TOP REINCIDENTES =====================
st.subheader("Top 10 reincidentes")
contagem = df_filtrado["chave_estabelecimento"].value_counts()
top10 = contagem[contagem > 1].head(10)

if top10.empty:
    st.info("Nenhum reincidente no filtro atual")
else:
    df_reincidentes = pd.DataFrame({
        "estabelecimento": [
            df_filtrado.loc[df_filtrado["chave_estabelecimento"] == k, "Distribuidora"].iloc[0].strip()[:40]
            for k in top10.index
        ],
        "tcis": top10.values
    })
    
    fig_reincidentes = px.bar(
        df_reincidentes,
        x="tcis",
        y="estabelecimento",
        orientation="h",
        text="tcis",
        height=460
    )
    fig_reincidentes.update_traces(textposition="outside")
    fig_reincidentes.update_layout(
        yaxis=dict(autorange="reversed", title=""),
        xaxis_title="Nº de TCIs",
        margin=dict(l=0, r=10, t=10, b=0),
        plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_reincidentes, width="stretch")

# ===================== EVOLUÇÃO MENSAL =====================
st.subheader("Evolução mensal")
serie = df_filtrado.groupby("mes").size().reset_index(name="tcis").sort_values("mes")

fig_serie = px.bar(
    serie,
    x="mes",
    y="tcis",
    text="tcis",
    height=420
)
fig_serie.update_traces(textposition="outside")
fig_serie.update_layout(
    xaxis_title="",
    yaxis_title="Nº de TCIs",
    margin=dict(l=0, r=0, t=10, b=0),
    plot_bgcolor="rgba(0,0,0,0)"
)
fig_serie.update_xaxes(dtick="M1", tickformat="%m-%Y")
st.plotly_chart(fig_serie, width="stretch")

# ===================== CATEGORIA =====================
col_cidade, col_bpm, col_infracao = st.columns([1.2, 1.2, 1])

with col_cidade:
    st.subheader("Por Cidade")
    por_cidade = df_filtrado["Cidade"].value_counts().head(15).reset_index()
    por_cidade.columns = ["cidade", "tcis"]
    fig_cidade = px.bar(
        por_cidade,
        x="tcis",
        y="cidade",
        orientation="h",
        height=420
    )
    fig_cidade.update_layout(
        yaxis=dict(autorange="reversed", title=""),
        xaxis_title="TCIs", 
        margin=dict(l=0, r=10, t=10, b=0),
        plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_cidade, width="stretch")

with col_bpm:
    st.subheader("Por Batalhão")
    por_bpm = df_filtrado["Batalhão"].value_counts().head(15).reset_index()
    por_bpm.columns = ["batalhao", "tcis"]
    fig_bpm = px.bar(
        por_bpm,
        x="tcis",
        y="batalhao",
        orientation="h",
        height=420
    )
    fig_bpm.update_layout(
        yaxis=dict(autorange="reversed", title=""),
        xaxis_title="TCIs", 
        margin=dict(l=0, r=10, t=10, b=0),
        plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_bpm, width="stretch")

with col_infracao:
    st.subheader("Tipo de Infração")
    por_infracao = df_filtrado["infracaoObservada"].value_counts().reset_index()
    por_infracao.columns = ["infracao", "tcis"]
    fig_infracao = px.pie(
        por_infracao,
        names="infracao",
        values="tcis",
        hole=0.55,
        height=420
    )
    fig_infracao.update_traces(textinfo="percent")
    fig_infracao.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", y=-0.1, font=dict(size=10)),
    )
    st.plotly_chart(fig_infracao, width="stretch")

st.dataframe(df_filtrado, width="stretch", hide_index=True)