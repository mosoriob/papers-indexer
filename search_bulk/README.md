S2 APIs involved:

- [GET /graph/v1/paper/search/bulk](https://api.semanticscholar.org/api-docs/graph#tag/Paper-Data/operation/get_graph_paper_bulk_search)

This example fetches a subset of paper data specified by a simple query and writes a JSON-lines archive of the results.

To run:

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
