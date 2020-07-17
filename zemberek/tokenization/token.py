from enum import Enum, auto


class Token:

    def __init__(self, content: str, type_: 'Token.Type', start: int, end: int, normalized: str = None):
        self.content = content
        self.type_ = type_
        self.start = start
        self.end = end
        self.normalized = self.content if normalized is None else normalized

    def __str__(self):
        return f"[{self.content} {self.type_} {self.start}-{self.end}]"

    class Type(Enum):
        SpaceTab = auto()
        NewLine = auto()
        Word = auto()
        WordAlphanumerical = auto()
        WordWithSymbol = auto()
        Abbreviation = auto()
        AbbreviationWithDots = auto()
        Punctuation = auto()
        RomanNumeral = auto()
        Number = auto()
        PercentNumeral = auto()
        Time = auto()
        Date = auto()
        URL = auto()
        Email = auto()
        HashTag = auto()
        Mention = auto()
        MetaTag = auto()
        Emoji = auto()
        Emoticon = auto()
        UnknownWord = auto()
        Unknown = auto()


