# Ingest paper metadata obtained from Semantic Scholar into a Neo4j database

This script reads a JSON archive of paper metadata obtained from Semantic Scholar and writes it to a Neo4j database.

## Usage

Parallel ingestion

```bash

python main-parallel.py --help
usage: main-parallel.py [-h] path

Create paper on Neo4j dataset

positional arguments:
  path        The file name or directory of the json file with the papers

options:
  -h, --help  show this help message and exit
```
