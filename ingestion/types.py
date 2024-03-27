from dataclasses import dataclass, asdict
from typing import Optional, List


@dataclass
class ExternalIds:
    MAG: str
    DOI: str
    CorpusId: int


@dataclass
class OpenAccessPdf:
    url: str
    status: str


@dataclass
class Journal:
    name: str
    pages: str
    volume: str

    def to_dict(self):
        return asdict(self)


@dataclass
class CitationStyles:
    bibtex: str


@dataclass
class Author:
    authorId: str
    name: str

    def to_dict(self):
        return asdict(self)


@dataclass
class S2FieldOfStudy:
    category: str
    source: str


@dataclass
class Venue:
    id: str
    name: str
    url: Optional[str] = None
    alternate_names: Optional[List[str]] = None
    issn: Optional[str] = None
    alternate_issns: Optional[List[str]] = None
    alternate_urls: Optional[List[str]] = None
    type: Optional[str] = None


@dataclass
class Paper:
    paperId: str
    externalIds: ExternalIds
    corpusId: int
    publicationVenue: Optional[Venue | str]
    url: str
    title: str
    abstract: Optional[str]
    venue: str
    year: int
    referenceCount: int
    citationCount: int
    influentialCitationCount: int
    isOpenAccess: bool
    openAccessPdf: OpenAccessPdf
    fieldsOfStudy: List[str]
    s2FieldsOfStudy: List[S2FieldOfStudy]
    publicationTypes: Optional[str]
    publicationDate: str
    journal: Journal
    citationStyles: CitationStyles
    authors: List[Author]

    def to_dict(self):
        publicationVenue = (
            self.publicationVenue
            if isinstance(self.publicationVenue, Venue)
            else self.publicationVenue
        )
        return {
            "paperId": self.paperId,
            "externalIds": self.externalIds,
            "corpusId": self.corpusId,
            "publicationVenue": publicationVenue,
            "url": self.url,
            "title": self.title,
            "abstract": self.abstract,
            "venue": self.venue,
            "year": self.year,
            "referenceCount": self.referenceCount,
            "citationCount": self.citationCount,
            "influentialCitationCount": self.influentialCitationCount,
            "isOpenAccess": self.isOpenAccess,
            "openAccessPdf": self.openAccessPdf,
            "fieldsOfStudy": self.fieldsOfStudy,
            "s2FieldsOfStudy": [s2 for s2 in self.s2FieldsOfStudy],
            "publicationTypes": self.publicationTypes,
            "publicationDate": self.publicationDate,
            # "journal": self.journal.to_dict(),
            "citationStyles": self.citationStyles,
            "authors": self.authors,
        }
