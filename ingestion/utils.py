from typing import Generator, Iterable, TypeVar
from itertools import islice

T = TypeVar("T")


def batched(iterable: Iterable[T], n: int) -> Generator[list[T], None, None]:
    "Batch data into tuples of length n. The last batch may be shorter."
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := list(islice(it, n)):
        yield batch
