import pandas as pd


def get_product_id(
    products: pd.DataFrame,
    product_name: str,
):
    matches = products[
        products["product_name"]
        .astype(str)
        .str.strip()
        .str.casefold()
        == product_name.strip().casefold()
    ]

    if matches.empty:
        raise ValueError(
            f"Produto não encontrado: {product_name}"
        )

    product_ids = matches["product_id"].drop_duplicates().tolist()

    if len(product_ids) > 1:
        raise ValueError(
            f"O nome {product_name!r} está associado a múltiplos IDs: "
            f"{product_ids}. Defina explicitamente a regra de consolidação."
        )

    return product_ids[0]


def rank_similar_products(
    target_product_id,
    similarity_matrix: pd.DataFrame,
    product_catalog: pd.DataFrame,
    top_n=5,
) -> pd.DataFrame:
    """
    Ordena produtos por similaridade decrescente,
    excluindo o próprio produto de referência.
    """

    if target_product_id not in similarity_matrix.index:
        raise KeyError(
            f"Produto {target_product_id} não encontrado "
            "na matriz de similaridade."
        )

    scores = (
        similarity_matrix.loc[target_product_id]
        .drop(labels=[target_product_id])
        .sort_values(ascending=False)
        .head(top_n)
        .rename("similarity")
        .reset_index()
    )

    scores.columns = ["product_id", "similarity"]

    catalog = (
        product_catalog[
            ["product_id", "product_name"]
        ]
        .drop_duplicates("product_id")
    )

    ranking = scores.merge(
        catalog,
        on="product_id",
        how="left",
        validate="one_to_one",
    )

    ranking.insert(
        0,
        "rank",
        range(1, len(ranking) + 1),
    )

    return ranking[
        ["rank", "product_id", "product_name", "similarity"]
    ]
