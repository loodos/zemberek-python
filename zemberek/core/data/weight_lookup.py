import numpy as np
from abc import ABC


class WeightLookup(ABC):

    def get_(self, key: str) -> np.float32:
        raise NotImplementedError()

    def size_(self) -> int:
        raise NotImplementedError()
