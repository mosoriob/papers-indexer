import os
from dotenv import load_dotenv
from neo4j import AsyncDriver

from ingestion.create_nodes_seq import (
    create_publication_venue_relation_paper,
)
from ingestion.query import (
    create_author_query,
    create_paper_query,
    create_publication_venue_query,
)
from ingestion.types import Author, Paper, Venue


load_dotenv(".env", override=True)
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE") or "neo4j"

AUTHENTATION = (NEO4J_USERNAME, NEO4J_PASSWORD)

if not NEO4J_URI:
    raise ValueError("Missing NEO4J_URI in environment")


async def create_node_tx(tx, paper: Paper) -> None:
    query = create_paper_query(paper)
    result = await tx.run(query, paper=paper.to_dict())
    node = await result.single()


async def create_author_node_tx(tx, author: Author) -> None:
    query = create_author_query()
    result = await tx.run(query, author=author)
    node = await result.single()


async def create_publication_venue_node_tx(tx, venue: Venue) -> None:
    query = create_publication_venue_query(venue)
    result = await tx.run(query, venue=venue)
    node = await result.single()


async def create_publication_venue_relation_paper_node_tx(
    tx, venue: Venue, paper: Paper
):
    query = create_publication_venue_relation_paper(venue, paper)
    result = await tx.run(query, venue=venue, paper=paper)
    node = await result.single()


async def create_paper_node(driver: AsyncDriver, paper: Paper):
    async with driver.session(database=NEO4J_DATABASE) as session:
        authors = paper.authors
        try:
            await session.write_transaction(create_node_tx, paper)

            if paper.publicationVenue is not None:
                venue = (
                    paper.publicationVenue
                    if isinstance(paper.publicationVenue, dict)
                    else paper.publicationVenue
                )

                if not isinstance(paper.publicationVenue, str) and isinstance(
                    venue, Venue
                ):
                    await session.write_transaction(
                        create_publication_venue_node_tx, venue=venue
                    )

                    await session.write_transaction(
                        create_publication_venue_relation_paper_node_tx,
                        venue=venue,
                        paper=paper,
                    )

            for author in authors:
                if author and author["authorId"] is not None:
                    await session.write_transaction(
                        create_author_node_tx, author=author
                    )
        except Exception as e:
            print(f"{paper.paperId}: {e}")
            session.cancel()
        finally:
            await session.close()
