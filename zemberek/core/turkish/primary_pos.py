from enum import Enum


class PrimaryPos(Enum):
    """
    An enum class that has the primary POS tags as members

    ...

    Methods
    -------
    get_string_form()
        Returns the short form of the POS tag,( value of member)
    """
    Noun = "Noun"
    Adjective = "Adj"
    Adverb = "Adv"
    Conjunction = "Conj"
    Interjection = "Interj"
    Verb = "Verb"
    Pronoun = "Pron"
    Numeral = "Num"
    Determiner = "Det"
    PostPositive = "Postp"
    Question = "Ques"
    Duplicator = "Dup"
    Punctuation = "Punc"
    Unknown = "Unk"

    def __init__(self, short_form: str):
        self.short_form = short_form

    def get_string_form(self) -> str:
        """
        returns the value of related member
        :return: short form of POS tag
        """
        return self.short_form

