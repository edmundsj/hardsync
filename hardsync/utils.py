import itertools
from typing import Sequence, List, TypeVar


T  = TypeVar('T')


def flatten(nested_list: Sequence[Sequence[T]]) -> List[T]:
    return list(itertools.chain.from_iterable(nested_list))
