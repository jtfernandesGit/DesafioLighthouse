
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="LH Nautical Analytics", page_icon="⚓", layout="wide")

DATA_DIR = Path("/workspace/data/raw")
PROCESSED_DIR = Path("/workspace/data/processed")
VALID_STATUSES = ["paid", "confirmed"]
FORECAST_PRODUCT = "Bússola de Bordo 702"
RECOMMENDATION_PRODUCT = "Motor de Popa 1949"


@st.cache_data
def load_data():
    files = {
        "products": DATA_DIR / "products.csv",
        "variants": DATA_DIR / "product_variants.csv",
        "orders": DATA_DIR / "orders.csv",
        "order_items": DATA_DIR / "order_items.csv",
    }
    missing = [str(p) for p in files.values() if not p.exists()]
    if missing:
        raise FileNotFoundError("Arquivos não encontrados:\n" + "\n".join(missing))

    return {
        "products": pd.read_csv(files["products"]),
        "variants": pd.read_csv(files["variants"]),
        "orders": pd.read_csv(files["orders"]),
        "order_items": pd.read_csv(files["order_items"]),
    }


def forecast_results(raw):
    products = raw["products"]
    variants = raw["variants"]
    orders = raw["orders"]
    order_items = raw["order_items"]

    target_products = products[
        products["name"].astype(str).str.strip().str.casefold()
        == FORECAST_PRODUCT.casefold()
    ]
    target_ids = target_products["id"].tolist()

    target_variants = (
        variants[variants["product_id"].isin(target_ids)][["id", "product_id"]]
        .rename(columns={"id": "product_variant_id"})
    )

    valid_orders = (
        orders[orders["status"].isin(VALID_STATUSES)][["id", "placed_at"]]
        .rename(columns={"id": "order_id", "placed_at": "order_date"})
    )

    items = order_items[
        order_items["product_variant_id"].isin(target_variants["product_variant_id"])
    ][["order_id", "product_variant_id", "quantity"]]

    unified = (
        items
        .merge(valid_orders, on="order_id", how="inner", validate="many_to_one")
        .merge(target_variants, on="product_variant_id", how="inner", validate="many_to_one")
    )

    unified["order_date"] = pd.to_datetime(unified["order_date"], errors="coerce")
    unified["quantity"] = pd.to_numeric(unified["quantity"], errors="coerce")
    unified = unified.dropna(subset=["order_date", "quantity"])
    unified["month"] = unified["order_date"].dt.to_period("M").dt.to_timestamp()

    monthly = (
        unified.groupby("month")["quantity"]
        .sum()
        .sort_index()
        .rename("actual")
        .to_frame()
    )

    full_range = pd.date_range(monthly.index.min(), monthly.index.max(), freq="MS")
    monthly = monthly.reindex(full_range, fill_value=0)
    monthly.index.name = "month"

    test_months = pd.date_range("2026-01-01", "2026-03-01", freq="MS")
    rows = []

    for month in test_months:
        previous = monthly.loc[monthly.index < month, "actual"].tail(3)
        forecast = previous.mean()
        actual = monthly.loc[month, "actual"]

        rows.append({
            "month": month,
            "forecast": float(forecast),
            "actual": float(actual),
            "absolute_error": float(abs(actual - forecast)),
        })

    result = pd.DataFrame(rows)
    mae = result["absolute_error"].mean()
    total = result["forecast"].sum()

    return monthly.reset_index(), result, mae, total


def recommendation_results(raw):
    products = raw["products"]
    variants = raw["variants"]
    orders = raw["orders"]
    order_items = raw["order_items"]

    processed = PROCESSED_DIR / "recommendation_interactions.csv"

    if processed.exists():
        interactions = pd.read_csv(processed)
    else:
        valid_orders = (
            orders[orders["status"].isin(VALID_STATUSES)][["id", "customer_id"]]
            .rename(columns={"id": "order_id"})
        )

        variant_lookup = (
            variants[["id", "product_id"]]
            .rename(columns={"id": "product_variant_id"})
        )

        product_lookup = (
            products[["id", "name"]]
            .rename(columns={"id": "product_id", "name": "product_name"})
        )

        interactions = (
            order_items[["order_id", "product_variant_id"]]
            .merge(valid_orders, on="order_id", how="inner", validate="many_to_one")
            .merge(variant_lookup, on="product_variant_id", how="inner", validate="many_to_one")
            .merge(product_lookup, on="product_id", how="inner", validate="many_to_one")
        )

        interactions = (
            interactions[["customer_id", "product_id", "product_name"]]
            .drop_duplicates(["customer_id", "product_id"])
        )
        interactions["purchased"] = 1

    matrix = interactions.pivot_table(
        index="customer_id",
        columns="product_id",
        values="purchased",
        aggfunc="max",
        fill_value=0,
    ).astype("int8")

    product_user = matrix.T
    similarity_values = cosine_similarity(product_user.values)
    similarity = pd.DataFrame(
        similarity_values,
        index=product_user.index,
        columns=product_user.index,
    )

    catalog = interactions[["product_id", "product_name"]].drop_duplicates()

    target = catalog[
        catalog["product_name"].astype(str).str.strip().str.casefold()
        == RECOMMENDATION_PRODUCT.casefold()
    ]

    target_id = target.iloc[0]["product_id"]

    scores = (
        similarity.loc[target_id]
        .drop(labels=[target_id])
        .sort_values(ascending=False)
        .head(5)
        .rename("similarity")
        .reset_index()
    )
    scores.columns = ["product_id", "similarity"]

    ranking = scores.merge(catalog, on="product_id", how="left")
    ranking.insert(0, "rank", range(1, len(ranking) + 1))

    return interactions, matrix, ranking


st.title("⚓ LH Nautical — Analytics Dashboard")
st.caption("Forecasting + Recommendation em uma única visão executiva.")

try:
    raw = load_data()
    monthly, forecast_df, mae, total_forecast = forecast_results(raw)
    interactions, matrix, ranking = recommendation_results(raw)
except Exception as exc:
    st.error("Falha ao carregar/processar os dados.")
    st.exception(exc)
    st.stop()

page = st.sidebar.radio(
    "Análise",
    ["Visão Geral", "Previsão de Demanda", "Sistema de Recomendação", "Qualidade dos Dados"]
)

if page == "Visão Geral":
    st.subheader("Resumo executivo")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Previsão Q1/2026", f"{round(total_forecast):.0f} un.")
    c2.metric("MAE", f"{mae:.2f} un.")
    c3.metric("Produto mais similar", ranking.iloc[0]["product_name"])
    c4.metric("Similaridade", f"{ranking.iloc[0]['similarity']:.4f}")

    left, right = st.columns(2)

    with left:
        chart_df = forecast_df.melt(
            id_vars="month",
            value_vars=["forecast", "actual"],
            var_name="series",
            value_name="units",
        )
        fig = px.line(
            chart_df, x="month", y="units", color="series", markers=True,
            title="Demanda — Real × Previsto"
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.bar(
            ranking.sort_values("similarity"),
            x="similarity",
            y="product_name",
            orientation="h",
            title="Top 5 similares ao Motor de Popa 1949",
        )
        st.plotly_chart(fig, use_container_width=True)

elif page == "Previsão de Demanda":
    st.subheader(f"Previsão de Demanda — {FORECAST_PRODUCT}")

    c1, c2 = st.columns(2)
    c1.metric("Previsão total Q1/2026", f"{total_forecast:.2f} un.")
    c2.metric("MAE", f"{mae:.2f} un.")

    shown = forecast_df.copy()
    shown["month"] = shown["month"].dt.strftime("%Y-%m")
    st.dataframe(shown, use_container_width=True, hide_index=True)

    fig = px.line(
        forecast_df.melt(
            id_vars="month",
            value_vars=["forecast", "actual"],
            var_name="series",
            value_name="units",
        ),
        x="month",
        y="units",
        color="series",
        markers=True,
        title="Real × Previsto — Q1/2026",
    )
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.line(
        monthly,
        x="month",
        y="actual",
        title=f"Histórico mensal — {FORECAST_PRODUCT}",
    )
    st.plotly_chart(fig2, use_container_width=True)

elif page == "Sistema de Recomendação":
    st.subheader(f"Recomendação — {RECOMMENDATION_PRODUCT}")

    top = ranking.iloc[0]

    c1, c2, c3 = st.columns(3)
    c1.metric("Produto recomendado", top["product_name"])
    c2.metric("Similaridade", f"{top['similarity']:.6f}")
    c3.metric("Produtos avaliados", f"{matrix.shape[1]}")

    st.dataframe(
        ranking[["rank", "product_id", "product_name", "similarity"]],
        use_container_width=True,
        hide_index=True,
    )

    fig = px.bar(
        ranking.sort_values("similarity"),
        x="similarity",
        y="product_name",
        orientation="h",
        title="Ranking de similaridade",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Amostra da matriz Usuário × Produto")
    st.caption(f"{matrix.shape[0]} clientes × {matrix.shape[1]} produtos")
    st.dataframe(matrix.iloc[:20, :20], use_container_width=True)

else:
    st.subheader("Qualidade dos Dados")

    orders = raw["orders"]
    products = raw["products"]
    variants = raw["variants"]
    order_items = raw["order_items"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pedidos", len(orders))
    c2.metric("Produtos", len(products))
    c3.metric("Variantes", len(variants))
    c4.metric("Itens", len(order_items))

    status_counts = orders["status"].value_counts().rename_axis("status").reset_index(name="orders")
    fig = px.bar(status_counts, x="status", y="orders", title="Status dos pedidos")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    **Regras aplicadas**
    - pedidos válidos: `paid` e `confirmed`;
    - forecast mensal;
    - recomendação binária por presença/ausência;
    - quantidade ignorada na matriz de recomendação;
    - variantes consolidadas no nível de produto.
    """)
