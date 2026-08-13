import sys
from pathlib import Path

import pandas as pd

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src"),
)

from recommender import rank_similar_products


def test_reference_product_is_removed_from_ranking():
    similarity = pd.DataFrame(
        [
            [1.0, 0.8, 0.2],
            [0.8, 1.0, 0.1],
            [0.2, 0.1, 1.0],
        ],
        index=[1, 2, 3],
        columns=[1, 2, 3],
    )

    catalog = pd.DataFrame(
        {
            "product_id": [1, 2, 3],
            "product_name": ["Motor", "Defensa", "Âncora"],
        }
    )

    ranking = rank_similar_products(
        target_product_id=1,
        similarity_matrix=similarity,
        product_catalog=catalog,
        top_n=2,
    )

    assert 1 not in ranking["product_id"].tolist()
    assert ranking.iloc[0]["product_id"] == 2
