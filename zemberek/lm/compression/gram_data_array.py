import numpy as np

from struct import unpack


class GramDataArray:
    MAX_BUF = 1073741823

    def __init__(self, file):
        self.count, self.fp_size, self.prob_size, self.backoff_size = unpack('>4i', file.read(4 * 4))
        self.fp_mask = 0  # this should be changed if default settings are changed
        """
        JAVA VERSION
        if (this.fpSize == 4) {
            this.fpMask = -1;
        } else {
            this.fpMask = (1 << this.fpSize * 8) - 1;
        }
        """

        self.block_size = self.fp_size + self.prob_size + self.backoff_size
        # page_length = self.get_power_of_two(k=self.MAX_BUF / self.block_size, limit=self.MAX_BUF / self.block_size)
        page_length = 536870912
        self.page_shift = 29
        self.index_mask = 268435455
        page_counter = 1

        self.data = []

        total = 0
        dt = np.dtype('>b')
        for i in range(page_counter):
            if i < (page_counter - 1):
                read_count = page_length * self.block_size
                total += page_length * self.block_size
            else:
                read_count = (self.count * self.block_size) - total

            self.data.append(np.fromfile(file, dtype=dt, count=read_count))

    @staticmethod
    def get_power_of_two(k: int, limit: int) -> int:
        if k <= 2:
            return 1
        else:
            i = 1
            while i < k:
                i = i * 2
            return i / 2 if i >= limit else i

    def get_probability_rank(self, index: int) -> int:
        page_id = index >> self.page_shift
        page_index = (index & self.index_mask) * self.block_size + self.fp_size

        d = self.data[page_id]
        if self.prob_size == 1:
            return d[page_index] & 255
        elif self.prob_size == 2:
            return (d[page_index] & 255) << 8 | d[page_index + 1] & 255
        elif self.prob_size == 3:
            return (d[page_index] & 255) << 16 | (d[page_index + 1] & 255) << 8 | d[page_index + 2] & 255
        else:
            return -1

    def get_back_off_rank(self, index: int) -> int:
        page_id = index >> self.page_shift
        page_index = (index & self.index_mask) * self.block_size + self.fp_size + self.prob_size

        d = self.data[page_id]
        if self.backoff_size == 1:
            return d[page_index] & 255
        elif self.backoff_size == 2:
            return (d[page_index] & 255) << 8 | d[page_index + 1] & 255
        elif self.backoff_size == 3:
            return (d[page_index] & 255) << 16 | (d[page_index + 1] & 255) << 8 | d[page_index + 2] & 255
        else:
            return -1

    def check_finger_print(self, fp_to_check_: int, global_index: int) -> bool:
        fp_to_check = fp_to_check_ & self.fp_mask
        page_index = (global_index & self.index_mask) * self.block_size
        d: bytes = self.data[global_index >> self.page_shift]

        if self.fp_size == 1:
            return fp_to_check == (d[page_index] & 0xFF)
        elif self.fp_size == 2:
            return (fp_to_check >> 8 == d[page_index] & 0xFF) and (fp_to_check & 0xFF == d[page_index + 1] & 0xFF)
        elif self.fp_size == 3:
            return (fp_to_check >> 16 == (d[page_index] & 0xFF)) \
                   and ((fp_to_check >> 8 & 0xFF) == (d[page_index + 1] & 0xFF)) \
                   and ((fp_to_check & 0xFF) == (d[page_index + 2] & 0xFF))
        elif self.fp_size == 4:
            return (fp_to_check >> 24 == (d[page_index] & 0xFF)) \
                   and ((fp_to_check >> 16 & 0xFF) == (d[page_index + 1] & 0xFF)) \
                   and ((fp_to_check >> 8 & 0xFF) == (d[page_index + 2] & 0xFF)) \
                   and ((fp_to_check & 0xFF) == (d[page_index + 3] & 0xFF))
        else:
            raise BaseException("fp_size must be between 1 and 4")
