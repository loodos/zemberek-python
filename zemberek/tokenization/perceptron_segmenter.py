import csv
import re

from pkg_resources import resource_filename
from typing import Dict, Set


class PerceptronSegmenter:
    r"""
        class that loads Binary Averaged Perceptron model and some rules-based approaches used in
        sentence boundary detection by TurkishSentenceExtractor class

        Attributes:
            web_words List[str]:
                Strings which are potentially representing a web site
            lowercase_vowels str:
                Lower cased vowels in Turkish alphabet
            uppercase_vowels str:
                Capital vowels in Turkish alphabet

    """

    web_words = ("http:", ".html", "www", ".tr", ".edu", "._zem.com", ".net", ".gov", "._zem.org", "@")
    lowercase_vowels = set("aeıioöuüâîû")
    uppercase_vowels = set("AEIİOÖUÜÂÎÛ")

    def __init__(self):
        self.turkish_abbreviation_set = self.load_abbreviations()
        pass

    @staticmethod
    def load_weights_from_csv(path: str = None) -> \
            Dict[str, float]:
        """
        function that loads model weights from csv file on given path
        csv file should be in this format:

        feature:str \t value:float

        :param path: path to csv file
        :return: a dictionary which holds hash values as keys and values as weights
        """
        if not path:
            path = resource_filename("zemberek", "resources/sentence_boundary_model_weights.csv")
        weights = dict()
        csv.field_size_limit(100000000)

        with open(path, 'r', encoding="utf-8") as f:
            lines = list(csv.reader(f, delimiter="\t"))

            for line in lines:
                weights[line[0]] = float(line[1])

        return weights

    @staticmethod
    def load_abbreviations(path: str = None) -> Set[str]:
        """
        function that loads Turkish abbreviations from a text file on given path It stores both
        original and lower cased version in a set

        :param path: text file that contains abbreviations as one abbreviation per line
        :return: set of strings storing both original and lower cased abbreviations
        """
        lower_map = {
            ord(u'I'): u'ı',
            ord(u'İ'): u'i',
        }

        if not path:
            path = resource_filename("zemberek", "resources/abbreviations.txt")

        abbr_set = set()
        with open(path, 'r', encoding="utf-8") as f:
            lines = list(f.readlines())
            for line in lines:
                if len(line.strip()) > 0:
                    abbr = re.sub(r'\s+', "", line.strip())
                    abbr_set.add(re.sub(r'\.$', "", abbr))
                    abbr = abbr.translate(lower_map)
                    abbr_set.add(re.sub(r'\.$', "", abbr.lower()))

        return abbr_set

    @classmethod
    def potential_website(cls, s: str) -> bool:
        for word in cls.web_words:
            if word in s:
                return True
        return False

    @classmethod
    def get_meta_char(cls, letter: str) -> str:
        """
        get meta char of a letter which will be used to get a specific weight value. Each return
        value is a special name the owners of the repo used in naming the features of perceptron

        :param letter: a letter to be checked
        :return: a specific character depending on the letter
        """
        if letter.isupper():
            c = 86 if letter in cls.uppercase_vowels else 67  # 86 -> 'V', 67 -> 'C'
        elif letter.islower():
            c = 118 if letter in cls.lowercase_vowels else 99  # 118 -> 'v', 99 -> 'c'
        elif letter.isdigit():
            c = 100  # 100 -> 'd'
        elif letter.isspace():
            c = 32  # 32 -> ' '
        elif letter == '.' or letter == '!' or letter == '?':
            return letter
        else:
            c = 45  # 45 -> '-'

        return chr(c)
