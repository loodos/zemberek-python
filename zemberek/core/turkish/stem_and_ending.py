class StemAndEnding:
    """
    A class to represent a word split as stem and ending. It the word is a stem, ending is empty string
    """
    def __init__(self, stem: str, ending: str):

        if not self.has_text(ending):
            ending = ""
        self.stem = stem
        self.ending = ending

    @staticmethod
    def has_text(s: str) -> bool:
        return s is not None and len(s) > 0 and len(s.strip()) > 0

    def __eq__(self, other):
        if self is other:
            return True
        elif other is not None and isinstance(other, StemAndEnding):
            if self.ending != other.ending:
                return False
            else:
                return self.stem == other.stem
        else:
            return False

    def __hash__(self):
        result = hash(self.stem) if self.stem is not None else 0
        result = 31 * result + (hash(self.ending) if self.ending is not None else 0)
        return result
