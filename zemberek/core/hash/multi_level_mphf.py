import numpy as np

from typing import List, BinaryIO, Tuple
from struct import unpack

from zemberek.core.hash.mphf import Mphf


class MultiLevelMphf(Mphf):
    """
    Minimum Perfect Hash Function Implementation. Detailed explanation can be found in original zemberek file
    """

    HASH_MULTIPLIER = 16777619
    INITIAL_HASH_SEED = 0x811C9DC5
    BIT_MASK_21 = (1 << 21) - 1

    def __init__(self, hash_level_data: Tuple['MultiLevelMphf.HashIndexes']):
        self.hash_level_data = hash_level_data

    @staticmethod
    def deserialize(f: BinaryIO) -> 'MultiLevelMphf':
        level_count, = unpack('>i', f.read(4))
        indexes: List['MultiLevelMphf.HashIndexes'] = []

        for i in range(level_count):
            key_count, = unpack('>i', f.read(4))
            bucket_amount, = unpack('>i', f.read(4))
            hash_seed_values: bytes = f.read(bucket_amount)
            failed_indexes_count, = unpack('>i', f.read(4))
            failed_indexes: np.ndarray = np.zeros(failed_indexes_count, dtype=np.int32)
            for j in range(failed_indexes_count):
                failed_indexes[j], = unpack('>i', f.read(4))

            indexes.append(MultiLevelMphf.HashIndexes(key_count, bucket_amount, hash_seed_values, failed_indexes))
        return MultiLevelMphf(tuple(indexes))

    @staticmethod
    def hash_(data: Tuple[int, ...], seed: int) -> int:
        d = seed if seed > 0 else MultiLevelMphf.INITIAL_HASH_SEED
        for a in data:
            d = (d ^ a) * MultiLevelMphf.HASH_MULTIPLIER

        return d & 0x7fffffff

    def get_(self, key: Tuple[int, ...], initial_hash: int) -> int:
        for i in range(len(self.hash_level_data)):
            seed = self.hash_level_data[i].get_seed(initial_hash)
            if seed != 0:
                if i == 0:
                    return self.hash_(key, seed) % self.hash_level_data[0].key_amount
                else:
                    return self.hash_level_data[i - 1].failed_indexes[self.hash_(key, seed) %
                                                                      self.hash_level_data[i].key_amount]
        raise BaseException("Cannot be here.")

    class HashIndexes:
        def __init__(self, key_amount: int, bucket_amount: int, bucket_hash_seed_values: bytes,
                     failed_indexes: np.ndarray):
            self.key_amount = key_amount
            self.bucket_amount = bucket_amount
            self.bucket_hash_seed_values = bucket_hash_seed_values
            self.failed_indexes = failed_indexes

        def get_seed(self, finger_print: int) -> int:
            return (self.bucket_hash_seed_values[finger_print % self.bucket_amount]) & 0xFF
