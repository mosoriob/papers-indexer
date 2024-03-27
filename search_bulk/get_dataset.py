import requests
import json
import os

from urllib3 import PoolManager
from urllib3.util.retry import Retry

retries = Retry(connect=5, read=2, redirect=5)

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
http = PoolManager(retries=retries)


def request_and_retry_timeout(url: str, retries: int = 3) -> dict | None:  # type: ignore
    response = http.request("GET", url)
    return json.loads(response.data.decode("utf-8"))


def get_papers_metadata(file_name: str, response: dict, url: str):  # type: ignore
    with open(file_name, "a") as file:
        retrieved: int = 0
        while True:
            if "data" in response:
                retrieved += len(response["data"])
                print(f"Retrieved {retrieved} papers...")
                for paper in response["data"]:
                    print(json.dumps(paper), file=file)
            elif "token" not in response:
                break
            response = request_and_retry_timeout(f"{url}&token={response['token']}")
        pass


def create_file_name(start_year: int, end_year: int):
    file_name = (
        f"papers-{start_year}.jsonl"
        if (start_year == end_year)
        else f"papers-{start_year}-{end_year }.jsonl"
    )
    return file_name


def search_paper_by_fields_years(
    fields: str, fieldsOfStudy: str, start_year: int, end_year: int, file_name: str
):
    url = f"http://api.semanticscholar.org/graph/v1/paper/search/bulk?fields={fields}&year={start_year}-{end_year}&fieldsOfStudy={fieldsOfStudy}&openAccessPdf"
    r = request_and_retry_timeout(url)
    if r is None or "error" in r:
        print(f"Failed to retrieve papers for {start_year} - {end_year}")
        print(r)
        exit(1)
    else:
        get_papers_metadata(file_name, r, url)
        print(f"{start_year} - {end_year} {r['total']}")


def convert_jsonl_to_json(file_name: str):
    with open(file_name, "r") as file:
        data = file.readlines()
        data = [json.loads(d) for d in data]
    with open(file_name.replace(".jsonl", ".json"), "w") as file:
        json.dump(data, file)


def trigger(
    start_year: int,
    end_year: int,
    fields: str,
    fieldsOfStudy: str,
    force: bool,
    destination: str,
):
    print("Searching papers for years", start_year, end_year)
    file_name = create_file_name(start_year, end_year)
    file_name = os.path.join(destination, file_name)
    if force and os.path.exists(file_name):
        os.remove(file_name)
    if not force and os.path.exists(file_name):
        print(f"File for {start_year} - {end_year} already exists, skipping...")
    else:
        search_paper_by_fields_years(
            fields, fieldsOfStudy, start_year, end_year, file_name
        )
        convert_jsonl_to_json(file_name)
        os.remove(file_name)
    start_year += jump


# python get_dataset.py 2023 2023

# parse arguments

import argparse

parser = argparse.ArgumentParser(description="Search papers in bulk")
parser.add_argument("start_year", type=int, help="Start year")
parser.add_argument("end_year", type=int, help="End year")
parser.add_argument("jump", type=int, help="How many years per file")
parser.add_argument("destination", type=str, help="Destination folder", default=".")
parser.add_argument(
    "--force", action="store_true", help="Force overwrite", default=False
)

args = parser.parse_args()
start_year_bulk = args.start_year
end_year_bulk = args.end_year
jump = args.jump
force = args.force
destination = args.destination


if not os.path.exists(destination):
    os.makedirs(destination)

fields = "paperId,corpusId,url,title,venue,publicationVenue,year,authors,externalIds,abstract,referenceCount,citationCount,influentialCitationCount,isOpenAccess,openAccessPdf,fieldsOfStudy,s2FieldsOfStudy,publicationTypes,publicationDate,journal,citationStyles"
# embedding,tldr"
fieldsOfStudy = "Materials Science"

if start_year_bulk > end_year_bulk:
    print("Start year should be less than end year")
    exit()

elif jump < 1:
    print("Jump should be greater than 0")
    exit()

elif jump - 1 > end_year_bulk - start_year_bulk:
    print("Jump should be less than the difference between start year and end year")
    exit()

elif start_year_bulk == end_year_bulk:
    trigger(start_year_bulk, end_year_bulk, fields, fieldsOfStudy, force, destination)

else:
    for start_year in range(start_year_bulk, end_year_bulk, jump):
        end_year = start_year + jump - 1
        trigger(start_year, end_year, fields, fieldsOfStudy, force, destination)
