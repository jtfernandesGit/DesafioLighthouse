up:
	docker compose up -d

down:
	docker compose down

schema:
	docker compose run --rm ingestion python src/ingestion/generate_schema.py

load:
	docker compose run --rm ingestion python src/ingestion/load_csv.py

test:
	docker compose run --rm ingestion pytest

logs:
	docker compose logs -f

#Bash Linux:

#make up
#make schema
#make load