from abc import ABC
from typing import Tuple


class Mphf(ABC):

    def get_(self, key: Tuple[int, ...], hash_: int) -> int:
        raise NotImplementedError

    @staticmethod
    def rshift(val: int, n: int) -> int:
        """Unsigned right shift operator

        :param int val: integer to be shifted to right
        :param int n: number of shifts
        :return: shifted value
        """
        return (val % 0x100000000) >> n
