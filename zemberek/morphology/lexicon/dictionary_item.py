from typing import Set

from zemberek.core.turkish import RootAttribute, PrimaryPos, SecondaryPos


class DictionaryItem:
    """
    A class used to represent a word and its properties
    in the lexicon dictionary

    ...

    Attributes
    ----------
    lemma : str
        the lemma of the word
    root : str
        the root of the word
    primary_pos : PrimaryPos
        primary POS tag assigned to the word
    secondary_pos : SecondaryPos
        secondary POS tag assigned to word if exists
        Default is SecondaryPos.None_
    attributes : Set[RootAttribute]
        attributes that are related to the word
    pronunciation : str
        pronunciation of the word. Default is None
    index : int
        non-unique index to words. Default is 0
    reference_item : DictionaryItem
        a reference object associated with current object

    Methods
    -------
    says(sound=None)
        Prints the animals name and what sound it makes
    """
    UNKNOWN: 'DictionaryItem'

    def __init__(self, lemma: str, root: str, primary_pos: PrimaryPos,
                 secondary_pos: SecondaryPos,  attributes: Set[RootAttribute] = None,
                 pronunciation: str = None, index: int = None):
        """
        Initializes a DictionaryItem object with given parameters that were read
        from lexicon

        :param lemma: lemma of the word
        :param root: root of the word
        :param primary_pos: primary POS tag for the word
        :param secondary_pos: secondary POS tag for the word
        :param attributes: set of predefined attributes given to word. Default is None
        :param pronunciation: pronunciation of the word. Default is None
        :param index: non-unique index for each word. Default is None
        """
        self.lemma = lemma
        self.root = root
        self.primary_pos = primary_pos
        self.secondary_pos = secondary_pos

        self.pronunciation = root if pronunciation is None else pronunciation
        self.index = 0 if index is None else index
        self.attributes = set() if attributes is None else attributes

        self.reference_item = None

        self.id_: str = self.generate_id(lemma, primary_pos, secondary_pos, self.index)

    @staticmethod
    def generate_id(lemma: str, pos: PrimaryPos, spos: SecondaryPos,
                    index: int) -> str:
        """
        generates and id for a word with given parameters
        generating formula is:

        word-lemma_word-ppos_word-spor_word-index

        kalem -> kalem_Noun_None_0

        :param lemma: lemma of the word
        :param pos: primary POS tag pre-assigned to word
        :param spos: secondary POS tag pre-assigned to word
        :param index: index of the word
        :return: generated string id
        """
        item_id = f"{lemma}_{pos.short_form}"

        if spos and spos != SecondaryPos.None_:
            item_id = f"{item_id}_{spos.short_form}"
        if index > 0:
            item_id = f"{item_id}_{str(index)}"
        return item_id

    def has_attribute(self, attribute: RootAttribute) -> bool:
        return attribute in self.attributes

    def set_reference_item(self, reference_item: 'DictionaryItem'):
        """
        sets a reference word for the given word
        :param reference_item: another DictinaryItem object aka another word
        related to current word
        """
        self.reference_item = reference_item

    def __str__(self):
        # return self.lemma + self.root + self.id
        string = self.lemma + " [P:" + self.primary_pos.short_form
        if self.secondary_pos and self.secondary_pos != SecondaryPos.None_:
            string += ", " + self.secondary_pos.short_form

        if self.attributes and len(self.attributes) == 0:
            string += "]"
        else:
            string = self.print_attributes(string, self.attributes)

        return string

    def normalized_lemma(self) -> str:
        return self.lemma[0: len(self.lemma) - 3] if self.primary_pos == PrimaryPos.Verb else self.lemma

    @staticmethod
    def print_attributes(string: str, attrs: Set[RootAttribute]) -> str:
        if attrs and len(attrs) > 0:
            string += "; A:"
            i = 0
            for attribute in attrs:
                string += attribute.name
                if i < len(attrs) - 1:
                    string += ", "
                i += 1
            string += "]"
        return string

    def is_unknown(self) -> bool:
        return self == DictionaryItem.UNKNOWN

    def __hash__(self):
        return hash(self.id_)

    def __eq__(self, other):
        if self is other:
            return True
        elif isinstance(other, DictionaryItem):
            return self.id_ == other.id_
        return False


DictionaryItem.UNKNOWN = DictionaryItem(lemma="UNK", root="UNK", pronunciation="UNK", primary_pos=PrimaryPos.Unknown,
                                        secondary_pos=SecondaryPos.UnknownSec)
