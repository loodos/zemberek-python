from typing import List
from struct import unpack

import numpy as np

class FloatLookup:
    def __init__(self, data: np.ndarray):  # data: Tuple[float]
        self.data = data
        self.range_ = data.shape[0]

    def change_self_base(self, source: float, target: float):
        multiplier = np.float32(np.log(source) / np.log(target))
        self.data *= multiplier

    @staticmethod
    def change_base(data: np.ndarray, source: float, target: float):
        multiplier = np.float32(np.log(source) / np.log(target))
        data *= multiplier

    @staticmethod
    def get_lookup_from_double(file) -> 'FloatLookup':
        range_, = unpack('>i', file.read(4))
        values = np.asarray(unpack('>{}d'.format(range_), file.read(range_ * 8)), dtype=np.float32)
        return FloatLookup(values)

    def get(self, n: int) -> np.float32:
        if 0 <= n < self.range_:
            return self.data[n]
        else:
            raise ValueError("Value is out of range")