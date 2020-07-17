from struct import unpack


class FloatLookup:
    def __init__(self, data):  # data: Tuple[float]
        self.data = data
        self.range_ = len(data)

    @staticmethod
    def get_lookup_from_double(file) -> 'FloatLookup':
        range_, = unpack('>i', file.read(4))
        values = tuple(unpack('>{}d'.format(range_), file.read(range_ * 8)))
        return FloatLookup(values)

    def get(self, n: int) -> float:
        if 0 <= n < self.range_:
            return self.data[n]
        else:
            raise ValueError("Value is out of range")