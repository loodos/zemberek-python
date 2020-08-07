import numpy as np

from typing import List, BinaryIO, Tuple
from struct import unpack

from zemberek.core.hash.mphf import Mphf
from zemberek.core.hash.multi_level_mphf import MultiLevelMphf


class LargeNgramMphf(Mphf):
    DEFAULT_CHUNK_SIZE_IN_BITS = 22

    def __init__(self, max_bit_mask: int, bucket_mask: int, page_shift: int, mphfs: Tuple[MultiLevelMphf],
                 offsets: np.ndarray):
        self.max_bit_mask = max_bit_mask
        self.bucket_mask = bucket_mask
        self.page_shift = page_shift
        self.mphfs = mphfs
        self.offsets = offsets

    @staticmethod
    def deserialize(f: BinaryIO) -> 'LargeNgramMphf':
        max_bit_mask, = unpack('>i', f.read(4))
        bucket_mask, = unpack('>i', f.read(4))
        page_shift, = unpack('>i', f.read(4))
        phf_count, = unpack('>i', f.read(4))

        offsets: np.ndarray = np.zeros(phf_count, dtype=np.int32)
        for i in range(phf_count):
            offsets[i], = unpack('>i', f.read(4))

        hashes: List[MultiLevelMphf] = []
        for i in range(phf_count):
            hashes.append(MultiLevelMphf.deserialize(f))

        return LargeNgramMphf(max_bit_mask, bucket_mask, page_shift, tuple(hashes), offsets)

    def get_(self, ngram: Tuple[int, ...], hash_: int) -> int:
        page_index = self.rshift(hash_ & self.max_bit_mask, self.page_shift)
        return self.mphfs[page_index].get_(ngram, hash_) + self.offsets[page_index]

