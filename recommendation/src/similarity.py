import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


def build_user_product_matrix(interactions: pd.DataFrame) -> pd.DataFrame:
    """
    Linhas: customer_id
    Colunas: product_id
    Valor: 1 se comprou ao menos uma vez, 0 caso contrário.
    """

    required = {"customer_id", "product_id", "purchased"}
    missing = required - set(interactions.columns)

    if missing:
        raise ValueError(
            f"Colunas obrigatórias ausentes: {sorted(missing)}"
        )

    matrix = interactions.pivot_table(
        index="customer_id",
        columns="product_id",
        values="purchased",
        aggfunc="max",
        fill_value=0,
    )

    return matrix.astype("int8")


def build_product_similarity(
    user_product_matrix: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calcula similaridade de cosseno produto x produto
    com base nos vetores de clientes.
    """

    product_user_matrix = user_product_matrix.T

    similarity_values = cosine_similarity(
        product_user_matrix.values
    )

    return pd.DataFrame(
        similarity_values,
        index=product_user_matrix.index,
        columns=product_user_matrix.index,
    )
