from abc import ABC
from typing import List


class Mphf(ABC):

    def get_(self, key: List[int], hash_: int) -> int:
        raise NotImplementedError
