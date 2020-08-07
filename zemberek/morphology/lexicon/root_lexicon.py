import csv
import time

from pkg_resources import resource_filename
from typing import List, Dict, Set, Tuple
from logging import Logger

from zemberek.core.turkish import RootAttribute, SecondaryPos, PrimaryPos
from zemberek.morphology.lexicon.dictionary_item import DictionaryItem

logger = Logger("logger")


class DictionaryReader:
    """
    A class that reads the lexicon into memory and creates a RootLexicon
    object

    ...

    Methods
    -------
    load_from_resources(resource_path: str) -> RootLexicon
        Reads the lexicon dictionary from lexicon.csv file in the given path

    """

    def __init__(self):
        pass

    @staticmethod
    def load_from_resources(resource_path: str) -> 'RootLexicon':
        """
        Reads the lexicon.csv file in the given path and creates and returns
        a RootLexicon object

        :param resource_path: path to the lexicon.csv file to be read
        :return: RootLexicon instance with the read lexicon dictionary
        """
        items = list()
        csv.field_size_limit(100000000)
        # relative path: os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), "resources/lexicon.csv"
        with open(resource_path, 'r', encoding='utf-8') as f:
            lex = list(csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE))

            for i, line in enumerate(lex):
                item = DictionaryReader.make_dict_item_from_line(line)
                if line[7] != 'null':
                    reference_item_line = None
                    iterator = iter(lex)
                    while reference_item_line is None:
                        line_ref = next(iterator)
                        if line[7] == line_ref[0]:
                            reference_item_line = line_ref
                    assert reference_item_line is not None
                    item.set_reference_item(DictionaryReader.make_dict_item_from_line(reference_item_line))

                items.append(item)
        return RootLexicon(items)

    @staticmethod
    def make_dict_item_from_line(line: List[str]) -> 'DictionaryItem':
        """
        Creates a DictionaryItem instance for a given lexicon.csv file line

        :param line: list of elements of a line in lexicon.csv file
        :return: a DictionaryItem instance with the parameters parsed from the line
        """
        item_lemma, item_root, item_pron = line[1], line[2], line[5]
        item_ppos, item_spos = PrimaryPos(line[3]), SecondaryPos(line[4])
        item_index = int(line[6])

        if line[8] == '0':
            item_attrs = None
        else:
            item_attrs = set([RootAttribute[attr] for attr in line[8].split()])

        return DictionaryItem(item_lemma, item_root, item_ppos, item_spos,
                              item_attrs, item_pron, item_index)


class DictionaryItemIterator:
    """
    An iterator class to iterate over RootLexicon instance

    Attributes
    ----------
    dict_items : Tuple[DictionaryItem]
        tuple of DictionaryItem (words) to iterate over
    index : int
        current item's position

    """

    def __init__(self, dict_items: Tuple[DictionaryItem]):
        self.dict_items = dict_items
        self.index = 0

    def __next__(self):
        """
        returns the next item from the list if exists
        else raises StopIteration exception
        :return: next item in the list
        """
        if self.index < len(self.dict_items):
            _item = self.dict_items[self.index]
            self.index += 1
            return _item
        raise StopIteration


class RootLexicon:
    """
    An iterable class to represent the lexicon dictionary

    Attributes
    ----------
    item_list : List[DictionaryItem]
        list of DictionaryItem (words) to store words read from a lexicon file
    """

    def __init__(self, item_list: List[DictionaryItem]):
        self.id_map: Dict[str, DictionaryItem] = dict()
        self.item_set: Set[DictionaryItem] = set()
        self.item_map: Dict[str, List[DictionaryItem]] = dict()
        for item in item_list:
            self.add_(item)

    def __len__(self):
        return len(self.item_set)

    def __iter__(self):
        return DictionaryItemIterator(tuple(self.item_set))

    def __contains__(self, item):
        return item in self.item_set

    def add_(self, item: DictionaryItem):
        if item in self.item_set:
            logger.warning("Duplicated item")
        elif item.id_ in self.id_map.keys():
            logger.warning(f"Duplicated item. ID {self.id_map.get(item.id_)}")
        else:
            self.item_set.add(item)
            self.id_map[item.id_] = item
            if item.lemma in self.item_map.keys():
                self.item_map[item.lemma].append(item)
            else:
                self.item_map[item.lemma] = [item]

    def get_item_by_id(self, id_: str) -> DictionaryItem:
        return self.id_map.get(id_)

    @staticmethod
    def get_default() -> 'RootLexicon':
        start = time.time()
        lexicon_path = resource_filename("zemberek", "resources/lexicon.csv")
        lexicon = DictionaryReader.load_from_resources(lexicon_path)
        logger.debug(f"Dictionary generated in {time.time() - start} seconds")
        return lexicon
