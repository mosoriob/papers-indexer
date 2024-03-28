import argparse
import asyncio
import json
import os
from typing import List

from dotenv import load_dotenv
from neo4j import AsyncGraphDatabase

from ingestion.create_nodes_parallel import create_paper_node
from ingestion.create_nodes_seq import (
    create_author_uniqueness_constraint,
    create_paper_uniqueness_constraint,
    create_publication_venue_uniqueness_constraint,
)
from ingestion.types import Paper


load_dotenv(".env", override=True)
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE") or "neo4j"
from typing import Generator, Iterable, TypeVar
from itertools import islice


if not NEO4J_URI:
    raise ValueError("Missing NEO4J_URI in environment")
    exit(1)

T = TypeVar("T")


def batched(iterable: Iterable[T], n: int) -> Generator[list[T], None, None]:
    "Batch data into tuples of length n. The last batch may be shorter."
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := list(islice(it, n)):
        yield batch


def parse_args():
    parser = argparse.ArgumentParser(description="Create paper on Neo4j dataset")
    parser.add_argument(
        "file_name",
        type=str,
        help="The file name of the json file with the papers",
    )
    return parser.parse_args()


async def create_nodes(data: List[dict]):  # type: ignore
    async with AsyncGraphDatabase.driver(
        NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
    ) as driver:
        counter = 0
        batchSize = 200
        length = len(data) // batchSize + 1
        for batch in batched(data, batchSize):
            counter += 1
            coroutines = [create_paper_node(driver, Paper(**item)) for item in batch]
            print("Processing batch ", counter, "/", length)
            await asyncio.gather(*coroutines)


def main():
    args = parse_args()
    file_name = args.file_name
    create_paper_uniqueness_constraint()
    create_author_uniqueness_constraint()
    create_publication_venue_uniqueness_constraint()

    with open(file_name, "r") as file:
        data = json.load(file)
    asyncio.run(create_nodes(data))


main()
