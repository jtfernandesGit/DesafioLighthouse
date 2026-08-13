import sys
from pathlib import Path

import pandas as pd

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src"),
)

from similarity import (
    build_user_product_matrix,
    build_product_similarity,
)


def test_user_product_matrix_is_binary():
    interactions = pd.DataFrame(
        {
            "customer_id": [1, 1, 2, 3],
            "product_id": [10, 20, 10, 20],
            "purchased": [1, 1, 1, 1],
        }
    )

    matrix = build_user_product_matrix(interactions)

    assert matrix.loc[1, 10] == 1
    assert matrix.loc[1, 20] == 1
    assert matrix.loc[2, 20] == 0
    assert set(matrix.stack().unique()).issubset({0, 1})


def test_identical_product_vectors_have_similarity_one():
    matrix = pd.DataFrame(
        {
            10: [1, 0, 1],
            20: [1, 0, 1],
        },
        index=[1, 2, 3],
    )

    similarity = build_product_similarity(matrix)

    assert round(similarity.loc[10, 20], 6) == 1.0
