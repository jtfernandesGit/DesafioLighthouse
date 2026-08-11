#!/usr/bin/env python3

"""
LH Nautical - CSV Loader

Responsabilidade:
    Carregar todos os arquivos CSV do diretório data/raw
    para o PostgreSQL na camada RAW.

Características:
    - Python 3
    - psycopg 3
    - PostgreSQL COPY
    - Não realiza transformação dos dados
    - Não remove valores nulos
    - Não corrige caracteres especiais
    - Não realiza deduplicação
    - Preserva os valores recebidos da fonte

Fluxo:

    CSV
      |
      v
    csv.reader()
      |
      v
    psycopg COPY / write_row()
      |
      v
    PostgreSQL
      |
      v
    raw.<table>

IMPORTANTE:

    O csv.reader() já interpreta o CSV.

    Por isso o COPY utiliza o formato TEXT padrão do
    PostgreSQL e NÃO utiliza:

        FORMAT CSV
        HEADER TRUE

    O header é removido pelo Python antes da carga.
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
    Escapa um identificador PostgreSQL.

    Exemplo:

        customers

    torna-se:

        "customers"

    Isso evita problemas com:
        - palavras reservadas
        - caracteres especiais
        - nomes incomuns de tabelas/colunas
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
    Converte o nome do arquivo em nome da tabela.

    Exemplo:

        customers.csv

    torna-se:

        customers
    """

    return csv_file.stem


# ============================================================
# CSV HEADER
# ============================================================

def read_header(csv_file: Path) -> list[str]:
    """
    Lê o header do CSV.

    Esta função é utilizada para validar que o arquivo
    possui um header antes da carga.
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

    return header


# ============================================================
# COPY COMMAND
# ============================================================

def build_copy_command(
    schema: str,
    table: str
) -> str:
    """
    Constrói o comando COPY do PostgreSQL.

    IMPORTANTE:

    O arquivo já foi interpretado pelo csv.reader().
    Portanto utilizamos o formato TEXT padrão do COPY.

    NÃO utilizamos:

        FORMAT CSV
        HEADER TRUE

    porque o psycopg copy.write_row() já envia os valores
    individualmente.
    """

    return (
        f"COPY "
        f"{quote_identifier(schema)}."
        f"{quote_identifier(table)} "
        f"FROM STDIN"
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
    Carrega um único arquivo CSV para o PostgreSQL.

    Retorna:
        quantidade de linhas carregadas.
    """

    table_name = table_name_from_file(
        csv_file
    )

    # --------------------------------------------------------
    # Validate header
    # --------------------------------------------------------

    header = read_header(
        csv_file
    )

    print(
        f"[LOAD] {csv_file.name} "
        f"-> {schema}.{table_name} "
        f"({len(header)} columns)"
    )

    # --------------------------------------------------------
    # Build COPY command
    # --------------------------------------------------------

    copy_command = build_copy_command(
        schema=schema,
        table=table_name
    )

    # --------------------------------------------------------
    # Start timer
    # --------------------------------------------------------

    start_time = time.perf_counter()

    rows_loaded = 0

    # --------------------------------------------------------
    # PostgreSQL COPY
    # --------------------------------------------------------

    with connection.cursor() as cursor:

        with cursor.copy(
            copy_command
        ) as copy:

            with csv_file.open(
                mode="r",
                encoding="utf-8-sig",
                newline=""
            ) as file:

                reader = csv.reader(
                    file
                )

                # ------------------------------------------------
                # Skip CSV header
                # ------------------------------------------------

                next(reader)

                # ------------------------------------------------
                # Load rows
                # ------------------------------------------------

                for row in reader:

                    # Não realizamos nenhuma transformação.

                    copy.write_row(
                        row
                    )

                    rows_loaded += 1

    # --------------------------------------------------------
    # Commit transaction
    # --------------------------------------------------------

    connection.commit()

    # --------------------------------------------------------
    # Performance information
    # --------------------------------------------------------

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

    Os arquivos são processados em ordem alfabética.
    """

    # --------------------------------------------------------
    # Validate directory
    # --------------------------------------------------------

    if not input_dir.exists():

        raise FileNotFoundError(
            f"Diretório não encontrado: {input_dir}"
        )

    # --------------------------------------------------------
    # Find CSV files
    # --------------------------------------------------------

    csv_files = sorted(
        input_dir.glob("*.csv")
    )

    if not csv_files:

        raise FileNotFoundError(
            f"Nenhum CSV encontrado em {input_dir}"
        )

    print(
        f"[INFO] Found {len(csv_files)} CSV files."
    )

    # --------------------------------------------------------
    # PostgreSQL connection string
    # --------------------------------------------------------

    connection_string = (
        f"host={DB_HOST} "
        f"port={DB_PORT} "
        f"dbname={DB_NAME} "
        f"user={DB_USER} "
        f"password={DB_PASSWORD}"
    )

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    results: dict[str, int] = {}

    # --------------------------------------------------------
    # Connect
    # --------------------------------------------------------

    print(
        "[INFO] Connecting to PostgreSQL..."
    )

    with psycopg.connect(
        connection_string
    ) as connection:

        print(
            "[INFO] PostgreSQL connection established."
        )

        # ----------------------------------------------------
        # Load each CSV
        # ----------------------------------------------------

        for csv_file in csv_files:

            table_name = table_name_from_file(
                csv_file
            )

            try:

                rows = load_csv(
                    connection=connection,
                    csv_file=csv_file,
                    schema=schema
                )

                results[table_name] = rows

            except Exception:

                # ------------------------------------------------
                # Rollback current transaction
                # ------------------------------------------------

                connection.rollback()

                raise

    return results


# ============================================================
# PRINT SUMMARY
# ============================================================

def print_summary(
    results: dict[str, int]
) -> None:
    """
    Exibe um resumo da carga.
    """

    print()

    print(
        "=" * 65
    )

    print(
        "LOAD SUMMARY"
    )

    print(
        "=" * 65
    )

    print(
        f"{'TABLE':<35}"
        f"{'ROWS':>15}"
    )

    print(
        "-" * 65
    )

    total_rows = 0

    for table_name, row_count in results.items():

        print(
            f"{table_name:<35}"
            f"{row_count:>15,}"
        )

        total_rows += row_count

    print(
        "-" * 65
    )

    print(
        f"{'TOTAL':<35}"
        f"{total_rows:>15,}"
    )

    print(
        "=" * 65
    )


# ============================================================
# CLI ARGUMENTS
# ============================================================

def parse_arguments() -> argparse.Namespace:
    """
    Processa os argumentos da linha de comando.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Load LH Nautical CSV files "
            "into PostgreSQL RAW."
        )
    )

    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help=(
            "Directory containing CSV files. "
            f"Default: {DEFAULT_INPUT_DIR}"
        )
    )

    parser.add_argument(
        "--schema",
        default=DEFAULT_SCHEMA,
        help=(
            "PostgreSQL schema. "
            f"Default: {DEFAULT_SCHEMA}"
        )
    )

    return parser.parse_args()


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    """
    Entry point da aplicação.
    """

    args = parse_arguments()

    try:

        results = load_all_csvs(
            input_dir=args.input_dir,
            schema=args.schema
        )

        print_summary(
            results
        )

        return 0

    except Exception as exc:

        print(
            f"[ERROR] {exc}",
            file=sys.stderr
        )

        return 1


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )

