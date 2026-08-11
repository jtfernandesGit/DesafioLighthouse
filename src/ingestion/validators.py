#!/usr/bin/env python3

"""
LH Nautical - CSV Loader

Responsabilidade:
    Carregar todos os CSVs do diretório data/raw para o
    PostgreSQL na camada RAW.

Características:
    - Python 3
    - psycopg 3
    - PostgreSQL COPY
    - Sem transformação dos valores
    - Sem remoção de nulos
    - Sem correção de caracteres
    - Sem deduplicação
    - Carga reproduzível

Fluxo:

    CSV
      ↓
    validators.py
      ↓
    PostgreSQL RAW
      ↓
    validation
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time

from pathlib import Path

import psycopg


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_INPUT_DIR = Path("data/raw")
DEFAULT_SCHEMA = "raw"


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_HOST = os.getenv(
    "DB_HOST",
    "postgres"
)

DB_PORT = os.getenv(
    "DB_PORT",
    "5432"
)

DB_NAME = os.getenv(
    "DB_NAME",
    "lh_nautical"
)

DB_USER = os.getenv(
    "DB_USER",
    "lh_admin"
)

DB_PASSWORD = os.getenv(
    "DB_PASSWORD",
    "lh_dev_password"
)


# ============================================================
# SQL IDENTIFIER
# ============================================================

def quote_identifier(identifier: str) -> str:
    """
    Escapa identificadores PostgreSQL.
    """

    escaped = identifier.replace(
        '"',
        '""'
    )

    return f'"{escaped}"'


# ============================================================
# TABLE NAME
# ============================================================

def table_name_from_file(csv_file: Path) -> str:
    """
    Converte:

        orders.csv

    em:

        orders
    """

    return csv_file.stem


# ============================================================
# READ HEADER
# ============================================================

def read_header(csv_file: Path) -> list[str]:
    """
    Lê o cabeçalho do CSV.
    """

    with csv_file.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.reader(file)

        try:
            header = next(reader)
        except StopIteration:
            raise ValueError(
                f"CSV vazio: {csv_file}"
            )

    if not header:

        raise ValueError(
            f"CSV sem header: {csv_file}"
        )

    return header


# ============================================================
# COPY COMMAND
# ============================================================

def build_copy_command(
    schema: str,
    table: str
) -> str:
    """
    Constrói o comando COPY utilizado pelo PostgreSQL.
    """

    return (
        f"COPY "
        f"{quote_identifier(schema)}."
        f"{quote_identifier(table)} "
        f"FROM STDIN "
        f"WITH (FORMAT CSV, HEADER TRUE)"
    )


# ============================================================
# LOAD SINGLE CSV
# ============================================================

def load_csv(
    connection: psycopg.Connection,
    csv_file: Path,
    schema: str
) -> int:
    """
    Carrega um CSV para uma tabela PostgreSQL.

    Retorna a quantidade de linhas carregadas.
    """

    table_name = table_name_from_file(
        csv_file
    )

    copy_command = build_copy_command(
        schema=schema,
        table=table_name
    )

    print(
        f"[LOAD] {csv_file.name} "
        f"-> {schema}.{table_name}"
    )

    start_time = time.perf_counter()

    rows_loaded = 0

    with connection.cursor() as cursor:

        with cursor.copy(copy_command) as copy:

            with csv_file.open(
                "r",
                encoding="utf-8-sig",
                newline=""
            ) as file:

                reader = csv.reader(file)

                # Ignora o header.
                next(reader)

                for row in reader:

                    # Mantemos os valores exatamente como
                    # vieram do CSV.
                    #
                    # Nenhum tratamento é realizado aqui.
                    copy.write_row(row)

                    rows_loaded += 1

    connection.commit()

    elapsed = (
        time.perf_counter()
        - start_time
    )

    print(
        f"[SUCCESS] {table_name}: "
        f"{rows_loaded:,} rows "
        f"in {elapsed:.2f}s"
    )

    return rows_loaded


# ============================================================
# LOAD ALL CSVs
# ============================================================

def load_all_csvs(
    input_dir: Path,
    schema: str
) -> dict[str, int]:
    """
    Carrega todos os CSVs encontrados no diretório.
    """

    csv_files = sorted(
        input_dir.glob("*.csv")
    )

    if not csv_files:

        raise FileNotFoundError(
            f"No CSV files found in {input_dir}"
        )

    connection_string = (
        f"host={DB_HOST} "
        f"port={DB_PORT} "
        f"dbname={DB_NAME} "
        f"user={DB_USER} "
        f"password={DB_PASSWORD}"
    )

    results = {}

    print(
        "[INFO] Connecting to PostgreSQL..."
    )

    with psycopg.connect(
        connection_string
    ) as connection:

        print(
            "[INFO] PostgreSQL connection established."
        )

        for csv_file in csv_files:

            table_name = table_name_from_file(
                csv_file
            )

            rows = load_csv(
                connection=connection,
                csv_file=csv_file,
                schema=schema
            )

            results[table_name] = rows

    return results


# ============================================================
# PRINT SUMMARY
# ============================================================

def print_summary(
    results: dict[str, int]
) -> None:

    print()
    print("=" * 60)
    print("LOAD SUMMARY")
    print("=" * 60)

    total_rows = 0

    for table_name, row_count in results.items():

        print(
            f"{table_name:<30}"
            f"{row_count:>15,}"
        )

        total_rows += row_count

    print("-" * 60)

    print(
        f"{'TOTAL':<30}"
        f"{total_rows:>15,}"
    )

    print("=" * 60)


# ============================================================
# CLI
# ============================================================

def parse_arguments():

    parser = argparse.ArgumentParser(
        description=(
            "Load LH Nautical CSV files into PostgreSQL."
        )
    )

    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR
    )

    parser.add_argument(
        "--schema",
        default=DEFAULT_SCHEMA
    )

    return parser.parse_args()


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    args = parse_arguments()

    try:

        results = load_all_csvs(
            input_dir=args.input_dir,
            schema=args.schema
        )

        print_summary(results)

        return 0

    except Exception as exc:

        print(
            f"[ERROR] {exc}",
            file=sys.stderr
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(main())