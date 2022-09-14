from __future__ import annotations

import numpy as np

from zemberek.core.data.weight_lookup import WeightLookup
from zemberek.core.compression.lossy_int_lookup import LossyIntLookup


class CompressedWeights(WeightLookup):

    def __init__(self, lookup: LossyIntLookup):
        self.lookup = lookup

    def size_(self) -> int:
        return self.lookup.size_()

    def get_(self, key: str) -> np.float32:
        return self.lookup.get_as_float(key)

    @classmethod
    def deserialize(cls, resource: str) -> 'CompressedWeights':
        with open(resource, 'rb') as dis:
            return cls(LossyIntLookup.deserialize(dis))
