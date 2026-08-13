from pathlib import Path
import pandas as pd

from dataset import build_and_save_interactions
from similarity import (
    build_user_product_matrix,
    build_product_similarity,
)
from recommender import (
    get_product_id,
    rank_similar_products,
)


TARGET_PRODUCT = "Motor de Popa 1949"
INTERACTIONS_PATH = Path(
    "/workspace/data/processed/recommendation_interactions.csv"
)


if __name__ == "__main__":
    if INTERACTIONS_PATH.exists():
        interactions = pd.read_csv(INTERACTIONS_PATH)
    else:
        interactions = build_and_save_interactions()

    product_catalog = (
        interactions[["product_id", "product_name"]]
        .drop_duplicates()
    )

    matrix = build_user_product_matrix(interactions)
    similarity = build_product_similarity(matrix)

    target_product_id = get_product_id(
        product_catalog,
        TARGET_PRODUCT,
    )

    ranking = rank_similar_products(
        target_product_id=target_product_id,
        similarity_matrix=similarity,
        product_catalog=product_catalog,
        top_n=5,
    )

    print(f"Produto de referência: {TARGET_PRODUCT}")
    print(ranking.to_string(index=False))
