from dataset import build_and_save_interactions


if __name__ == "__main__":
    interactions = build_and_save_interactions()

    print(
        "Dataset salvo em "
        "/workspace/data/processed/recommendation_interactions.csv"
    )
    print(f"Interações únicas: {len(interactions):,}")
    print(
        f"Clientes: {interactions['customer_id'].nunique():,}"
    )
    print(
        f"Produtos: {interactions['product_id'].nunique():,}"
    )
