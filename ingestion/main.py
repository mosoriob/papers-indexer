from dataclasses import asdict
from dotenv import load_dotenv
import os

# Common data processing
import json
import argparse
from ingestion.types import Author, Paper, Venue

load_dotenv(".env", override=True)
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE") or "neo4j"

from langchain_community.graphs import Neo4jGraph

kg = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    database=NEO4J_DATABASE,
)


def create_author(author: Author):
    cypher = """
    MERGE (author:Author {authorId: $author.authorId})
        ON CREATE
            SET author.name = $author.name,
                author.authorId = $author.authorId
    """
    kg.query(cypher, params={"author": author})
    return cypher


def create_author_uniqueness_constraint():
    cypher = """
    CREATE CONSTRAINT unique_author IF NOT EXISTS
    FOR (a:Author) REQUIRE a.author IS UNIQUE
    """
    kg.query(cypher)
    return cypher


def create_paper(paper: Paper):
    cypher = """
    MERGE (paper:Paper {paperId: $paper.paperId})
        ON CREATE
            SET paper.title = $paper.title,
                paper.externalIdMag = $paper.externalIds.MAG,
                paper.externalIdDoi = $paper.externalIds.DOI,
                paper.externalIdCorpus = $paper.externalIds.CorpusId,
                paper.corpusId = $paper.corpusId,
                """
    if isinstance(paper.publicationVenue, str):
        cypher += "paper.publicationVenue = $paper.publicationVenue"

    cypher += """
                paper.url = $paper.url,
                paper.venue = $paper.venue,
                paper.year = $paper.year,
                paper.referenceCount = $paper.referenceCount,
                paper.citationCount = $paper.citationCount,
                paper.influentialCitationCount = $paper.influentialCitationCount,
                paper.isOpenAccess = $paper.isOpenAccess,
                paper.openAccessPdfUrl = $paper.openAccessPdf.url,
                paper.openAccessPdfStatus = $paper.openAccessPdf.status,
                paper.fieldsOfStudy = $paper.fieldsOfStudy,
                paper.publicationTypes = $paper.publicationTypes,
                paper.publicationDate = $paper.publicationDate

    """
    kg.query(cypher, params={"paper": paper.to_dict()})
    return cypher


def create_paper_uniqueness_constraint():
    cypher = """
    CREATE CONSTRAINT unique_paper IF NOT EXISTS
    FOR (p:Paper) REQUIRE p.paperId IS UNIQUE
    """
    kg.query(cypher)
    return cypher


def create_relation_paper_author(paperId: str, authorId: str):
    cypher = """
    MATCH (paper:Paper {paperId: $paperId})
    MATCH (author:Author {authorId: $authorId})
    MERGE (author)-[:IS_AUTHOR]->(paper)
    """
    kg.query(cypher, params={"paperId": paperId, "authorId": authorId})
    return cypher


def create_publication_venue(venue: Venue):
    cypher = """
    MERGE (venue:Venue {venueId: $venue.id})
        ON CREATE
            SET venue.id = $venue.id,
                venue.name = $venue.name,
                venue.type = $venue.type,
                venue.alternate_names = $venue.alternate_names,
                venue.url = $venue.url
    """
    kg.query(cypher, params={"venue": asdict(venue)})


def create_publication_venue_uniqueness_constraint():
    cypher = """
    CREATE CONSTRAINT unique_venue IF NOT EXISTS
    FOR (v:Venue) REQUIRE v.venueId IS UNIQUE
    """
    kg.query(cypher)
    return cypher


def create_publication_venue_relation_paper(venue: Venue, paper: Paper):
    cypher = """
    MATCH (venue:Venue {venueId: $venueId})
    MATCH (paper:Paper {paperId: $paperId})
    MERGE (paper)-[:WAS_PUBLISHED]->(venue)
    """
    kg.query(cypher, params={"venueId": venue.id, "paperId": paper.paperId})
    return cypher


# Path: ingestion/main.py
# Create paper on Neo4j dataset
# It reads a json file using the dataclasses.Paper class and creates
# a node on the Neo4j database


def create_uniquess_constraints():
    create_author_uniqueness_constraint()
    create_paper_uniqueness_constraint()
    create_publication_venue_uniqueness_constraint()


def create_nodes(file_name: str):
    create_author_uniqueness_constraint()
    with open(file_name, "r") as file:
        data = json.load(file)

    for paper in data:
        paper = Paper(**paper)
        authors = paper.authors
        create_paper(paper)
        if paper.publicationVenue is not None:
            venue = (
                Venue(**paper.publicationVenue)
                if isinstance(paper.publicationVenue, dict)
                else paper.publicationVenue
            )

            if not isinstance(paper.publicationVenue, str) and isinstance(venue, Venue):
                create_publication_venue(venue)
                create_publication_venue_relation_paper(venue, paper)

        for author in authors:
            if author and author["authorId"] is not None:
                create_author(author)
                create_relation_paper_author(paper.paperId, author["authorId"])


def parse_args():
    parser = argparse.ArgumentParser(description="Create paper on Neo4j dataset")
    parser.add_argument(
        "file_name",
        type=str,
        help="The file name of the json file with the papers",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    create_nodes(args.file_name)


main()
