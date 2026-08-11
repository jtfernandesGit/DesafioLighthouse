#!/usr/bin/env python3

"""
LH Nautical - Raw Schema Generator

Responsabilidade:
    Descobrir os arquivos CSV presentes no diretório de dados
    e gerar um único arquivo schema.sql contendo as instruções
    CREATE TABLE para PostgreSQL.

Princípios:
    - Python 3
    - Somente biblioteca padrão
    - Não utiliza pandas/polars/dask
    - Não altera os dados
    - RAW utiliza TEXT para preservar o conteúdo original
    - Identificadores SQL são devidamente escapados
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_INPUT_DIR = Path("data/raw")
DEFAULT_OUTPUT_FILE = Path("sql/01_raw/schema.sql")
DEFAULT_SCHEMA = "raw"


# ============================================================
# SQL IDENTIFIER
# ============================================================

def quote_identifier(identifier: str) -> str:
    """
    Escapa um identificador PostgreSQL.

    Exemplo:

        customer_id
        ↓
        "customer_id"

    Isso permite lidar com nomes contendo:
        - espaços
        - caracteres especiais
        - palavras reservadas
    """

    escaped = identifier.replace('"', '""')

    return f'"{escaped}"'


# ============================================================
# TABLE NAME
# ============================================================

def table_name_from_file(csv_file: Path) -> str:
    """
    Converte:

        customers.csv

    em:

        customers
    """

    return csv_file.stem


# ============================================================
# CSV HEADER
# ============================================================

def read_header(csv_file: Path) -> list[str]:
    """
    Lê somente o header do CSV.

    Não carrega o arquivo inteiro em memória.
    """

    with csv_file.open(
        mode="r",
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
            f"CSV sem colunas: {csv_file}"
        )

    # Detecta nomes vazios.
    empty_columns = [
        index
        for index, column in enumerate(header)
        if not column.strip()
    ]

    if empty_columns:
        raise ValueError(
            f"{csv_file}: colunas vazias nas posições "
            f"{empty_columns}"
        )

    # Detecta colunas duplicadas.
    duplicates = {
        column
        for column in header
        if header.count(column) > 1
    }

    if duplicates:
        raise ValueError(
            f"{csv_file}: colunas duplicadas: "
            f"{sorted(duplicates)}"
        )

    return header


# ============================================================
# CREATE TABLE
# ============================================================

def generate_create_table(
    csv_file: Path,
    schema: str
) -> str:
    """
    Gera o CREATE TABLE correspondente ao CSV.

    Todos os campos são TEXT na camada RAW.
    """

    table_name = table_name_from_file(csv_file)

    header = read_header(csv_file)

    columns = []

    for column in header:

        columns.append(
            f"    {quote_identifier(column)} TEXT"
        )

    columns_sql = ",\n".join(columns)

    return f"""
CREATE TABLE IF NOT EXISTS {quote_identifier(schema)}.{quote_identifier(table_name)}
(
{columns_sql}
);
""".strip()


# ============================================================
# GENERATE SCHEMA
# ============================================================

def generate_schema(
    input_dir: Path,
    output_file: Path,
    schema: str
) -> None:
    """
    Descobre todos os CSVs e gera schema.sql.
    """

    if not input_dir.exists():
        raise FileNotFoundError(
            f"Diretório não encontrado: {input_dir}"
        )

    csv_files = sorted(
        input_dir.glob("*.csv")
    )

    if not csv_files:
        raise FileNotFoundError(
            f"Nenhum CSV encontrado em {input_dir}"
        )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    sql_sections = []

    sql_sections.append(
        f"""-- ============================================================
-- LH NAUTICAL - RAW SCHEMA
-- ============================================================
--
-- Arquivo gerado automaticamente por generate_schema.py
--
-- Camada RAW:
--     Os dados são preservados sem transformação.
--
-- Os campos são armazenados como TEXT propositalmente.
-- Conversões de tipo devem ocorrer posteriormente na camada
-- STAGING.
--
-- Generated tables:
-- """
    )

    for csv_file in csv_files:

        table_name = table_name_from_file(csv_file)

        sql_sections.append(
            f"--     {table_name}"
        )

    sql_sections.append(
        f"""
-- ============================================================

CREATE SCHEMA IF NOT EXISTS {quote_identifier(schema)};
"""
    )

    for csv_file in csv_files:

        create_table_sql = generate_create_table(
            csv_file=csv_file,
            schema=schema
        )

        sql_sections.append(
            f"""
-- ============================================================
-- SOURCE: {csv_file.name}
-- ============================================================

{create_table_sql}
"""
        )

    output_file.write_text(
        "\n".join(sql_sections),
        encoding="utf-8"
    )

    print(
        f"Schema generated successfully: {output_file}"
    )

    print(
        f"Tables generated: {len(csv_files)}"
    )


# ============================================================
# CLI
# ============================================================

def parse_arguments() -> argparse.Namespace:

    parser = argparse.ArgumentParser(
        description=(
            "Generate PostgreSQL RAW schema from CSV files."
        )
    )

    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help=(
            "Directory containing CSV files "
            f"(default: {DEFAULT_INPUT_DIR})"
        )
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_FILE,
        help=(
            "Output SQL file "
            f"(default: {DEFAULT_OUTPUT_FILE})"
        )
    )

    parser.add_argument(
        "--schema",
        default=DEFAULT_SCHEMA,
        help=(
            "PostgreSQL schema name "
            f"(default: {DEFAULT_SCHEMA})"
        )
    )

    return parser.parse_args()


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    args = parse_arguments()

    try:

        generate_schema(
            input_dir=args.input_dir,
            output_file=args.output,
            schema=args.schema
        )

        return 0

    except Exception as exc:

        print(
            f"ERROR: {exc}",
            file=sys.stderr
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(main())