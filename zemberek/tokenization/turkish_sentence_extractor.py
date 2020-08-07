import re

from typing import List, Dict, Set, Tuple

from zemberek.core.turkish import TurkishAlphabet
from zemberek.tokenization.perceptron_segmenter import PerceptronSegmenter
from zemberek.tokenization.span import Span


class TurkishSentenceExtractor(PerceptronSegmenter):
    r"""
        A class that separates sentences by processing them with both
        perceptron model which it inherits from PerceptronSegmenter class and
        ruled based approaches

        Args:
            do_not_split_in_double_quotes bool:

        Attributes:
            BOUNDARY_CHARS str:
                most frequently used sentence ending characters
            double_quotes str:
                special quoting characters
    """

    BOUNDARY_CHARS = set(".!?…")
    double_quotes = set("\"”“»«")

    def __init__(self, do_not_split_in_double_quotes: bool = False):
        super().__init__()
        self.weights: Dict[str, float] = self.load_weights_from_csv()
        self.do_not_split_in_double_quotes = do_not_split_in_double_quotes
        self.abbr_set = self.load_abbreviations()

    def extract_to_spans(self, paragraph: str) -> List[Span]:
        """
        function that divides paragraph into spans depending on whether feature related to
        the current character of the paragraph contribute to the overall score which is used
        to determine if the span is sentence or not
        :param paragraph: string containing a paragraph to which will be divided
        :return: the list of strings of potential sentences
        """
        spans = []
        quote_spans = None

        # if self.do_not_split_in_double_quotes:
        #    quote_spans = self.double_quote_spans(paragraph)

        begin = 0

        for j, ch in enumerate(paragraph):
            if ch in self.BOUNDARY_CHARS and \
                 (not self.do_not_split_in_double_quotes or quote_spans is None or not self.in_span(j, quote_spans)):
                boundary_data = TurkishSentenceExtractor.BoundaryData(paragraph, j, self.abbr_set)
                if not boundary_data.non_boundary_check():
                    features = boundary_data.extract_features()
                    score = 0.0

                    for feature in features:
                        score += self.get_weight(feature)

                    if score > 0.0:
                        span = Span(begin, j + 1)
                        if span.get_length() > 0:
                            spans.append(span)
                        begin = j + 1

        if begin < len(paragraph):
            span = Span(begin, len(paragraph))
            if span.get_length() > 0:
                spans.append(span)

        return spans

    def from_paragraph(self, paragraph: str) -> List[str]:
        """
        function that extracts the potential sentences from paragraph
        :param paragraph: string that holds paragraph to be analyzed
        :return: the list of sentences extracted from paragraph
        """
        spans = self.extract_to_spans(paragraph)
        sentences = []
        for span_ in spans:
            sentence = span_.get_sub_string(paragraph).strip()
            if len(sentence) > 0:
                sentences.append(sentence)

        return sentences

    @staticmethod
    def in_span(index: int, spans: List[Span]) -> bool:
        """
        function that checks whether the specified index is in any of the spans
        that were previously found
        :param index: index value to be checked
        :param spans: list of spans already found
        :return: returns true if the index falls into boundaries of any span, false otherwise
        """
        for span_ in spans:
            if span_.start > index:
                return False
            if span_.in_span(index):
                return True

        return False

    def get_weight(self, key: str) -> float:
        if key in self.weights.keys():
            return self.weights[key]
        return 0.0

    class BoundaryData:
        r"""
            Class that represents various features for the character specified with index of a string
            It uses previous and next unigram/bigram characters related to current character, finds previous
            and next boundary characters (space or one od BOUNDARY_CHARS), current word, previous and next
            parts of the word related to the current char, current word with no punctuations, and next word.

        """
        def __init__(self, input_string: str, pointer: int, abbr_set: Set[str]):
            self.previous_letter = input_string[pointer-1] if pointer > 0 else '_'
            self.next_letter = input_string[pointer+1] if pointer < (len(input_string) - 1) else '_'
            self.previous_two_letters = input_string[pointer-2:pointer] if pointer > 2 else '__'
            self.next_two_letters = input_string[pointer+1:pointer+3] if pointer < (len(input_string) - 3) else '__'
            self.previous_space = self.find_backwards_space_or_char(input_string, pointer)
            self.left_chunk = input_string[self.previous_space:pointer]
            self.previous_boundary_or_space = self.find_backwards_space_or_char(input_string, pointer, '.')
            self.left_chunk_until_boundary = self.left_chunk if self.previous_space == self.previous_boundary_or_space \
                else input_string[self.previous_boundary_or_space:pointer]

            self.next_space = self.find_forwards_space_or_char(input_string, pointer)
            self.right_chunk = input_string[pointer+1:self.next_space] if pointer < (len(input_string) - 1) else ""
            self.next_boundary_or_space = self.find_forwards_space_or_char(input_string, pointer, '.')
            self.right_chunk_until_boundary = self.right_chunk if self.next_space == self.next_boundary_or_space \
                else input_string[pointer+1:self.next_boundary_or_space]

            self.current_char = input_string[pointer]
            self.current_word = self.left_chunk + self.current_char + self.right_chunk
            self.current_word_no_punctuation = re.sub(r"[.!?…]", "", self.current_word)

            next_word_exists = input_string[self.next_space+1:].find(' ')
            if next_word_exists == -1:  # no space character ahead
                self.next_word = input_string[self.next_space+1:]
            else:
                self.next_word = input_string[self.next_space+1: next_word_exists]

            self.abbr_set = abbr_set

        @staticmethod
        def find_backwards_space_or_char(string: str, pos: int, char: str = ' ') -> int:

            for i in range(pos - 1, -1, -1):
                if string[i] == ' ' or string[i] == char:
                    return i + 1
            return 0

        @staticmethod
        def find_forwards_space_or_char(string: str, pos: int, char: str = ' '):

            for i in range(pos + 1, len(string)):
                if string[i] == ' ' or string[i] == char:
                    return i
            return len(string)

        def non_boundary_check(self) -> bool:
            """
            function that checks the current word or char is a potential sentence boundary
            :return:
            """
            return len(self.left_chunk_until_boundary) == 1 or self.next_letter == '\'' or \
                self.next_letter in TurkishSentenceExtractor.BOUNDARY_CHARS or \
                self.current_word in self.abbr_set or self.left_chunk_until_boundary in self.abbr_set or \
                PerceptronSegmenter.potential_website(self.current_word)

        def extract_features(self) -> Tuple[str]:
            """
            function that extracts features from according to a set of rules defined by the owner of
            this repository. Each feature extracted in this method has a learned weight in
            TurkishSentenceExtractor.weights
            :return: the list of features extracted from current position of the paragraph
            """
            features = list()
            features.append("1:" + ("true" if self.previous_letter.isupper() else "false"))
            features.append("1b:" + ("true" if self.next_letter.isspace() else "false"))
            features.append("1a:" + self.previous_letter)
            features.append("1b:" + self.next_letter)
            features.append("2p:" + self.previous_two_letters)
            features.append("2n:" + self.next_two_letters)
            if len(self.current_word) > 0:
                features.append("7c:" + ("true" if self.current_word[0].isupper() else "false"))
                features.append("9c:" + PerceptronSegmenter.get_meta_char(self.current_word))

            if len(self.right_chunk) > 0:
                features.append("7r:" + ("true" if self.right_chunk[0].isupper() else "false"))
                features.append("9r:" + PerceptronSegmenter.get_meta_char(self.right_chunk))

            if len(self.left_chunk) > 0 and not TurkishAlphabet.INSTANCE.contains_vowel(self.left_chunk):
                features.append("lcc:true")

            if len(self.current_word_no_punctuation) > 0:
                all_up = True
                all_digit = True

                for c in self.current_word_no_punctuation:
                    if not c.isupper():
                        all_up = False
                    if not c.isdigit():
                        all_digit = False

                if all_up:
                    features.append("11u:true")
                if all_digit:
                    features.append("11d:true")

            return tuple(features)
