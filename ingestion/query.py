from ingestion.types import Paper, Venue


def create_paper_query(paper: Paper):
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
                paper.abstract = $paper.abstract,
                paper.influentialCitationCount = $paper.influentialCitationCount,
                paper.isOpenAccess = $paper.isOpenAccess,
                paper.openAccessPdfUrl = $paper.openAccessPdf.url,
                paper.openAccessPdfStatus = $paper.openAccessPdf.status,
                paper.fieldsOfStudy = $paper.fieldsOfStudy,
                paper.publicationTypes = $paper.publicationTypes,
                paper.publicationDate = $paper.publicationDate

        RETURN paper.paperId as id
    """

    return cypher


def create_publication_venue_query(venue: Venue):
    return """
    MERGE (venue:Venue {venueId: $venue.id})
        ON CREATE
            SET venue.id = $venue.id,
                venue.name = $venue.name,
                venue.type = $venue.type,
                venue.alternate_names = $venue.alternate_names,
                venue.url = $venue.url
    """


def create_relation_paper_author_query(paperId: str, authorId: str):
    return """
    MATCH (paper:Paper {paperId: $paperId})
    MATCH (author:Author {authorId: $authorId})
    MERGE (author)-[:IS_AUTHOR]->(paper)
    """


def create_author_query():
    return """
    MERGE (author:Author {authorId: $author.authorId})
        ON CREATE
            SET author.name = $author.name,
                author.authorId = $author.authorId
    """


def create_author_uniqueness_constraint_query():
    return """
    CREATE CONSTRAINT unique_author IF NOT EXISTS
    FOR (a:Author) REQUIRE a.author IS UNIQUE
    """


def create_paper_uniqueness_constraint_query():
    return """
    CREATE CONSTRAINT unique_paper IF NOT EXISTS
    FOR (p:Paper) REQUIRE p.paperId IS UNIQUE
    """


def create_publication_venue_uniqueness_constraint_query():
    return """
    CREATE CONSTRAINT unique_venue IF NOT EXISTS
    FOR (v:Venue) REQUIRE v.venueId IS UNIQUE
    """


def create_publication_venue_relation_paper_query():
    return """
    MATCH (venue:Venue {venueId: $venueId})
    MATCH (paper:Paper {paperId: $paperId})
    MERGE (paper)-[:WAS_PUBLISHED]->(venue)
    """
