# Semantic Scholar Ingestion into Neo4j

The repository contains two scripts to ingest paper metadata obtained from Semantic Scholar into a Neo4j database. The scripts are:

1. [search_bulk/get_dataset.py](search_bulk/get_dataset.py): Fetches a subset of paper data specified by a simple query and writes a JSON archive of the results.
2. [ingestion/main-parallel.py](ingestion/main-parallel.py): Reads a JSON archive of paper metadata obtained from Semantic Scholar and writes it to a Neo4j database.

## Usage

### Fetching paper metadata

To fetch paper metadata, run the following command:

```
python get_dataset.py
usage: get_dataset.py [-h] [--force] start_year end_year jump destination

Search papers in bulk

positional arguments:
  start_year   Start year
  end_year     End year
  jump         How many years per file
  destination  Destination folder

options:
  -h, --help   show this help message and exit
  --force      Force overwrite existing files
```

### Ingesting paper metadata

To ingest paper metadata into a Neo4j database, run the following command:

```bash

python main-parallel.py --help
usage: main-parallel.py [-h] path

Create paper on Neo4j dataset

positional arguments:
  path        The file name or directory of the json file with the papers

options:
  -h, --help  show this help message and exit
```
