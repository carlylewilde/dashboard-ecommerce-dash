from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html
from scipy.stats import gaussian_kde


# Caminho absoluto baseado na pasta do próprio app.py.
# Assim, o CSV é encontrado tanto no PyCharm quanto no servidor de publicação.
BASE_DIR = Path(__file__).resolve().parent
ARQUIVO_DADOS = BASE_DIR / "ecommerce_estatistica.csv"


def carregar_dados() -> pd.DataFrame:
    """Lê e prepara os dados usados pelo dashboard."""
    dados = pd.read_csv(ARQUIVO_DADOS)

    # A primeira coluna veio do índice salvo no CSV e não possui valor analítico.
    dados = dados.drop(columns=["Unnamed: 0"], errors="ignore")

    colunas_numericas = [
        "Nota",
        "N_Avaliações",
        "Desconto",
        "Preço",
        "Qtd_Vendidos_Cod",
    ]
    dados[colunas_numericas] = dados[colunas_numericas].apply(
        pd.to_numeric, errors="coerce"
    )
    return dados.dropna(subset=colunas_numericas)


df = carregar_dados()

CORES = ["#6f2dbd", "#a663cc", "#ffb703", "#219ebc", "#8ecae6", "#fb8500"]
TEMPLATE = "plotly_white"


def aplicar_estilo(fig: go.Figure, titulo_x: str, titulo_y: str) -> go.Figure:
    """Aplica o mesmo padrão visual a todos os gráficos."""
    fig.update_layout(
        template=TEMPLATE,
        margin=dict(l=40, r=25, t=70, b=45),
        title_x=0.03,
        font=dict(family="Arial", color="#201335"),
        legend_title_text="",
        hoverlabel=dict(bgcolor="white"),
    )
    fig.update_xaxes(title=titulo_x, gridcolor="#eee9f5")
    fig.update_yaxes(title=titulo_y, gridcolor="#eee9f5")
    return fig


def filtrar_dados(generos, marcas) -> pd.DataFrame:
    """Retorna uma cópia filtrada sem alterar o DataFrame original."""
    filtrado = df.copy()
    if generos:
        filtrado = filtrado[filtrado["Gênero"].isin(generos)]
    if marcas:
        filtrado = filtrado[filtrado["Marca"].isin(marcas)]
    return filtrado


def grafico_histograma(dados: pd.DataFrame) -> go.Figure:
    fig = px.histogram(
        dados,
        x="Preço",
        nbins=20,
        color_discrete_sequence=[CORES[0]],
        title="Distribuição dos preços dos produtos",
    )
    return aplicar_estilo(fig, "Preço (R$)", "Quantidade de produtos")


def grafico_dispersao(dados: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        dados,
        x="Preço",
        y="Nota",
        color="Gênero",
        size="N_Avaliações",
        hover_name="Título",
        hover_data={"Desconto": ":.0f", "N_Avaliações": ":.0f"},
        color_discrete_sequence=CORES,
        title="Preço, nota e volume de avaliações",
    )
    return aplicar_estilo(fig, "Preço (R$)", "Nota média")


def grafico_mapa_calor(dados: pd.DataFrame) -> go.Figure:
    colunas = ["Preço", "Nota", "Desconto", "N_Avaliações", "Qtd_Vendidos_Cod"]
    correlacao = dados[colunas].corr(method="pearson")
    rotulos = ["Preço", "Nota", "Desconto", "Avaliações", "Qtd. vendida"]
    fig = px.imshow(
        correlacao,
        x=rotulos,
        y=rotulos,
        text_auto=".2f",
        zmin=-1,
        zmax=1,
        color_continuous_scale="RdBu_r",
        title="Mapa de calor das correlações de Pearson",
    )
    return aplicar_estilo(fig, "Variáveis", "Variáveis")


def grafico_barras(dados: pd.DataFrame) -> go.Figure:
    marcas = (
        dados.groupby("Marca", as_index=False)
        .agg(Produtos=("Título", "count"), Nota_média=("Nota", "mean"))
        .sort_values("Produtos", ascending=False)
        .head(12)
    )
    fig = px.bar(
        marcas,
        x="Marca",
        y="Produtos",
        color="Nota_média",
        color_continuous_scale="Purples",
        text_auto=True,
        title="Marcas com maior quantidade de produtos",
    )
    return aplicar_estilo(fig, "Marca", "Quantidade de produtos")


def grafico_pizza(dados: pd.DataFrame) -> go.Figure:
    generos = dados["Gênero"].value_counts().rename_axis("Gênero").reset_index(name="Produtos")
    fig = px.pie(
        generos,
        names="Gênero",
        values="Produtos",
        hole=0.42,
        color_discrete_sequence=CORES,
        title="Participação dos produtos por gênero",
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return aplicar_estilo(fig, "", "")


def grafico_densidade(dados: pd.DataFrame) -> go.Figure:
    precos = dados["Preço"].dropna().to_numpy()
    fig = go.Figure()

    if len(precos) >= 2 and np.ptp(precos) > 0:
        eixo_x = np.linspace(precos.min(), precos.max(), 250)
        densidade = gaussian_kde(precos)(eixo_x)
        fig.add_trace(
            go.Scatter(
                x=eixo_x,
                y=densidade,
                mode="lines",
                fill="tozeroy",
                name="Densidade",
                line=dict(color=CORES[1], width=3),
                hovertemplate="Preço: R$ %{x:.2f}<br>Densidade: %{y:.4f}<extra></extra>",
            )
        )
    else:
        fig.add_annotation(text="Dados insuficientes para calcular a densidade", showarrow=False)

    fig.update_layout(title="Densidade estimada dos preços")
    return aplicar_estilo(fig, "Preço (R$)", "Densidade")


def grafico_regressao(dados: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        dados,
        x="N_Avaliações",
        y="Qtd_Vendidos_Cod",
        hover_name="Título",
        color_discrete_sequence=[CORES[3]],
        title="Regressão: avaliações e quantidade vendida",
    )

    if len(dados) >= 2 and dados["N_Avaliações"].nunique() > 1:
        x = dados["N_Avaliações"].to_numpy()
        y = dados["Qtd_Vendidos_Cod"].to_numpy()
        coef_angular, intercepto = np.polyfit(x, y, 1)
        x_linha = np.linspace(x.min(), x.max(), 100)
        y_linha = coef_angular * x_linha + intercepto
        fig.add_trace(
            go.Scatter(
                x=x_linha,
                y=y_linha,
                mode="lines",
                name="Tendência linear",
                line=dict(color=CORES[5], width=3),
            )
        )

    return aplicar_estilo(fig, "Número de avaliações", "Quantidade vendida (codificada)")


app = Dash(__name__)
server = app.server  # Necessário para publicação com Gunicorn/Render.
app.title = "Dashboard de E-commerce"


def cartao_indicador(titulo: str, identificador: str):
    return html.Div(
        [html.P(titulo, className="kpi-label"), html.H3(id=identificador, className="kpi-value")],
        className="kpi-card",
    )


app.layout = html.Div(
    [
        html.Header(
            [
                html.P("PROJETO FINAL • VISUALIZAÇÃO AVANÇADA", className="eyebrow"),
                html.H1("Dashboard de E-commerce"),
                html.P(
                    "Explore preços, avaliações, descontos, marcas e vendas sem precisar executar código Python.",
                    className="subtitle",
                ),
            ],
            className="hero",
        ),
        html.Main(
            [
                html.Section(
                    [
                        html.Div(
                            [
                                html.Label("Filtrar por gênero"),
                                dcc.Dropdown(
                                    id="filtro-genero",
                                    options=[{"label": x, "value": x} for x in sorted(df["Gênero"].unique())],
                                    multi=True,
                                    placeholder="Todos os gêneros",
                                ),
                            ],
                            className="filter-block",
                        ),
                        html.Div(
                            [
                                html.Label("Filtrar por marca"),
                                dcc.Dropdown(
                                    id="filtro-marca",
                                    options=[{"label": x.title(), "value": x} for x in sorted(df["Marca"].unique())],
                                    multi=True,
                                    placeholder="Todas as marcas",
                                ),
                            ],
                            className="filter-block",
                        ),
                    ],
                    className="filters-card",
                ),
                html.Section(
                    [
                        cartao_indicador("Produtos", "kpi-produtos"),
                        cartao_indicador("Preço médio", "kpi-preco"),
                        cartao_indicador("Nota média", "kpi-nota"),
                        cartao_indicador("Desconto médio", "kpi-desconto"),
                    ],
                    className="kpi-grid",
                ),
                html.P(id="aviso-filtro", className="filter-warning"),
                dcc.Loading(
                    html.Section(
                        [
                            dcc.Graph(id="grafico-histograma", className="chart-card"),
                            dcc.Graph(id="grafico-dispersao", className="chart-card"),
                            dcc.Graph(id="grafico-calor", className="chart-card"),
                            dcc.Graph(id="grafico-barras", className="chart-card"),
                            dcc.Graph(id="grafico-pizza", className="chart-card"),
                            dcc.Graph(id="grafico-densidade", className="chart-card"),
                            dcc.Graph(id="grafico-regressao", className="chart-card chart-wide"),
                        ],
                        className="charts-grid",
                    ),
                    type="circle",
                    color=CORES[0],
                ),
            ],
            className="page-container",
        ),
        html.Footer("Projeto acadêmico desenvolvido com Pandas, Plotly e Dash."),
    ]
)


@app.callback(
    Output("kpi-produtos", "children"),
    Output("kpi-preco", "children"),
    Output("kpi-nota", "children"),
    Output("kpi-desconto", "children"),
    Output("aviso-filtro", "children"),
    Output("grafico-histograma", "figure"),
    Output("grafico-dispersao", "figure"),
    Output("grafico-calor", "figure"),
    Output("grafico-barras", "figure"),
    Output("grafico-pizza", "figure"),
    Output("grafico-densidade", "figure"),
    Output("grafico-regressao", "figure"),
    Input("filtro-genero", "value"),
    Input("filtro-marca", "value"),
)
def atualizar_dashboard(generos, marcas):
    dados = filtrar_dados(generos, marcas)

    if dados.empty:
        dados = df.copy()
        aviso = "A combinação selecionada não possui registros. Exibindo todos os dados."
    else:
        aviso = f"Exibindo {len(dados)} de {len(df)} produtos."

    return (
        f"{len(dados):,}".replace(",", "."),
        f"R$ {dados['Preço'].mean():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        f"{dados['Nota'].mean():.2f}".replace(".", ","),
        f"{dados['Desconto'].mean():.1f}%".replace(".", ","),
        aviso,
        grafico_histograma(dados),
        grafico_dispersao(dados),
        grafico_mapa_calor(dados),
        grafico_barras(dados),
        grafico_pizza(dados),
        grafico_densidade(dados),
        grafico_regressao(dados),
    )


if __name__ == "__main__":
    app.run(debug=True)
