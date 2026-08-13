from pathlib import Path
import pandas as pd


VALID_STATUSES = ("paid", "confirmed")


def load_raw_data(data_dir="/workspace/data/raw"):
    data_dir = Path(data_dir)

    files = {
        "products": data_dir / "products.csv",
        "variants": data_dir / "product_variants.csv",
        "orders": data_dir / "orders.csv",
        "order_items": data_dir / "order_items.csv",
    }

    missing = [str(path) for path in files.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Arquivos não encontrados:\n" + "\n".join(missing)
        )

    return {
        "products": pd.read_csv(files["products"]),
        "variants": pd.read_csv(files["variants"]),
        "orders": pd.read_csv(files["orders"]),
        "order_items": pd.read_csv(files["order_items"]),
    }


def build_interaction_dataset(
    products: pd.DataFrame,
    variants: pd.DataFrame,
    orders: pd.DataFrame,
    order_items: pd.DataFrame,
    valid_statuses=VALID_STATUSES,
) -> pd.DataFrame:
    """
    Cria um dataset cliente-produto em nível de presença/ausência.

    Cada par customer_id-product_id aparece no máximo uma vez.
    Quantidade comprada é deliberadamente ignorada.
    """

    valid_orders = (
        orders.loc[
            orders["status"].isin(valid_statuses),
            ["id", "customer_id"],
        ]
        .rename(columns={"id": "order_id"})
        .copy()
    )

    variant_lookup = (
        variants[["id", "product_id"]]
        .rename(columns={"id": "product_variant_id"})
        .copy()
    )

    product_lookup = (
        products[["id", "name"]]
        .rename(
            columns={
                "id": "product_id",
                "name": "product_name",
            }
        )
        .copy()
    )

    interactions = (
        order_items[["order_id", "product_variant_id"]]
        .merge(
            valid_orders,
            on="order_id",
            how="inner",
            validate="many_to_one",
        )
        .merge(
            variant_lookup,
            on="product_variant_id",
            how="inner",
            validate="many_to_one",
        )
        .merge(
            product_lookup,
            on="product_id",
            how="inner",
            validate="many_to_one",
        )
    )

    interactions = (
        interactions[
            ["customer_id", "product_id", "product_name"]
        ]
        .drop_duplicates(["customer_id", "product_id"])
        .sort_values(["customer_id", "product_id"])
        .reset_index(drop=True)
    )

    interactions["purchased"] = 1

    return interactions


def build_and_save_interactions(
    data_dir="/workspace/data/raw",
    output_path="/workspace/data/processed/recommendation_interactions.csv",
):
    raw = load_raw_data(data_dir)

    interactions = build_interaction_dataset(
        products=raw["products"],
        variants=raw["variants"],
        orders=raw["orders"],
        order_items=raw["order_items"],
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    interactions.to_csv(output_path, index=False)

    return interactions
