import re


class TextUtil:

    @staticmethod
    def normalize_apostrophes(inp: str):
        """Convert different apostrophe symbols to a unified form

        :param str inp: text to be processed
        :return: cleaned input string
        """
        return re.sub(r'[′´`’‘]', "'", inp)

    @staticmethod
    def normalize_quotes_hyphens(inp: str) -> str:
        inp_ = re.sub(r"[“”»«″]|''", "\"", inp)
        inp_ = re.sub(r"[′´`’‘]", "'", inp_)
        inp_ = re.sub(r"[–]", "-", inp_)
        return inp_

