# DesafioLighthouse
Desafio Dados e IA programa Lighthouse

Pipeline planejado para o projeto 

1. Docker
   ↓
2. PostgreSQL
   ↓
3. Validação dos CSVs
   ↓
4. Geração do schema
   ↓
5. Criação das tabelas RAW
   ↓
6. Carga dos CSVs
   ↓
7. Validação pós-carga
   ↓
8. EDA / Q1
   ↓
9. Análises SQL / Q4-Q5
   ↓
10. Modelagem / Q6
   ↓
11. Recomendação / Q7
   ↓
12. Dashboard

#### 1.Construir as imagens Docker
 `docker compose build` 

#### 2.Subir ambiente
 `docker compose up -d`

#### 3.Validação arquivos CSV (camada raw)
`docker compose exec ingestion \
    python src/ingestion/validators.py`

#### 4.Gerar o schema
`docker compose exec ingestion \
    python src/ingestion/generate_schema.py`

### 5.Criar as tabelas no Postgres 
`docker compose exec -T postgres \
    psql \
    -U lh_admin \
    -d lh_nautical \
    < sql/01_raw/schema.sql`    

#### 6.Carregar CSVs 
`docker compose exec ingestion \
    python src/ingestion/load_csv.py` 

#### 7.Validar a carga de dados com uma consulta sql
`docker compose exec postgres \
    psql \
    -U lh_admin \
    -d lh_nautical \
    -c "SELECT COUNT(*) FROM raw.customers;"`

