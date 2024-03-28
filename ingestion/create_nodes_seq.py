from dataclasses import asdict
from dotenv import load_dotenv
import os

from ingestion.query import (
    create_author_query,
    create_author_uniqueness_constraint_query,
    create_paper_query,
    create_paper_uniqueness_constraint_query,
    create_publication_venue_query,
    create_publication_venue_relation_paper_query,
    create_publication_venue_uniqueness_constraint_query,
    create_relation_paper_author_query,
)
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
    cypher = create_author_query()
    kg.query(cypher, params={"author": author})
    return cypher


def create_author_uniqueness_constraint():
    cypher = create_author_uniqueness_constraint_query()
    kg.query(cypher)
    return cypher


def create_paper(paper: Paper):
    cypher = create_paper_query(paper)
    kg.query(cypher, params={"paper": paper.to_dict()})
    return cypher


def create_paper_uniqueness_constraint():
    cypher = create_paper_uniqueness_constraint_query()
    kg.query(cypher)
    return cypher


def create_relation_paper_author(paperId: str, authorId: str):
    cypher = create_relation_paper_author_query(paperId, authorId)
    kg.query(cypher, params={"paperId": paperId, "authorId": authorId})
    return cypher


def create_publication_venue(venue: Venue):
    cypher = create_publication_venue_query(venue)
    kg.query(cypher, params={"venue": asdict(venue)})


def create_publication_venue_uniqueness_constraint():
    cypher = create_publication_venue_uniqueness_constraint_query()
    kg.query(cypher)
    return cypher


def create_publication_venue_relation_paper(venue: Venue, paper: Paper):
    cypher = create_publication_venue_relation_paper_query()
    kg.query(cypher, params={"venueId": venue.id, "paperId": paper.paperId})
    return cypher
