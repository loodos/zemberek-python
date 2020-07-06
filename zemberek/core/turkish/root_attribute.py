from enum import Enum, auto


class RootAttribute(Enum):
    """
    An enum class to represent attributes of a root

    ...

    Methods
    -------
    get_string_form(sound=None)
        Returns the name of the class member
    """

    Aorist_I = auto()
    Aorist_A = auto()
    ProgressiveVowelDrop = auto()
    Passive_In = auto()
    Causative_t = auto()
    Voicing = auto()
    NoVoicing = auto()
    InverseHarmony = auto()
    Doubling = auto()
    LastVowelDrop = auto()
    CompoundP3sg = auto()
    NoSuffix = auto()
    NounConsInsert_n = auto()
    NoQuote = auto()
    CompoundP3sgRoot = auto()
    Reflexive = auto()
    Reciprocal = auto()
    NonReciprocal = auto()
    Ext = auto()
    Runtime = auto()
    Dummy = auto()
    ImplicitDative = auto()
    ImplicitPlural = auto()
    ImplicitP1sg = auto()
    ImplicitP2sg = auto()
    FamilyMember = auto()
    PronunciationGuessed = auto()
    Informal = auto()
    LocaleEn = auto()
    Unknown = auto()

    def get_string_form(self) -> str:
        return self.name
