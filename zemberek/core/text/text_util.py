import re


class TextUtil:

    @staticmethod
    def normalize_apostrophes(inp: str):
        return re.sub(r'[′´`’‘]', "'", inp)
