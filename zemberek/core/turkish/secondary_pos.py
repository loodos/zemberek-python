from enum import Enum


class SecondaryPos(Enum):
    """
    An enum class that has secondary POS tags as members

    ...

    Methods
    -------
    get_string_form()
        Returns the short form of POS tag
    """

    UnknownSec = "Unk"
    DemonstrativePron = "Demons"
    Time = "Time"
    QuantitivePron = "Quant"
    QuestionPron = "Ques"
    ProperNoun = "Prop"
    PersonalPron = "Pers"
    ReflexivePron = "Reflex"
    None_ = "None"
    Ordinal = "Ord"
    Cardinal = "Card"
    Percentage = "Percent"
    Ratio = "Ratio"
    Range = "Range"
    Real = "Real"
    Distribution = "Dist"
    Clock = "Clock"
    Date = "Date"
    Email = "Email"
    Url = "Url"
    Mention = "Mention"
    HashTag = "HashTag"
    Emoticon = "Emoticon"
    RomanNumeral = "RomanNumeral"
    RegularAbbreviation = "RegAbbrv"
    Abbreviation = "Abbrv"
    PCDat = "PCDat"
    PCAcc = "PCAcc"
    PCIns = "PCIns"
    PCNom = "PCNom"
    PCGen = "PCGen"
    PCAbl = "PCAbl"

    def __init__(self, short_form: str):
        self.short_form = short_form

    def get_string_form(self) -> str:
        """
        returns the value of related member
        :return: short form of POS tag
        """
        return self.short_form
