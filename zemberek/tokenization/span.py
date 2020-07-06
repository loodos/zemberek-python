class Span:
    r"""
        A class that represents specified chunks of a string. It is used to divide
        TurkishSentenceExtractor input paragraphs into smaller pieces from which the
        features will be extracted.
    """
    def __init__(self, start: int, end: int):
        if start >= 0 and end >= 0:
            if end < start:
                raise Exception("Span end value can not be smaller than start value")
            else:
                self.start = start
                self.end = end
        else:
            raise Exception("Span start and end values can not be negative")

    def get_length(self) -> int:
        return self.end - self.start

    def middle_value(self) -> int:
        # THIS METHOD IS WRONG, CHECK THE USAGE
        return self.end + (self.end - self.start) // 2

    def get_sub_string(self, string: str) -> str:
        return string[self.start:self.end]

    def in_span(self, i: int) -> bool:
        return self.start <= i < self.end

    def copy(self, offset: int) -> 'Span':
        return Span(offset + self.start, offset + self.end)
