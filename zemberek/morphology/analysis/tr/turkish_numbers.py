import re

from pkg_resources import resource_filename
from typing import List, Tuple, Dict


class TurkishNumbers:
    NUMBER_SEPARATION = re.compile("[0-9]+|[^0-9 ]+")
    thousands: Tuple[str] = ("", "bin", "milyon", "milyar", "trilyon", "katrilyon")
    single_digit_numbers: Tuple[str] = ("", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz")
    ten_to_ninety: Tuple[str] = ("", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan")
    roman_numeral_pattern = re.compile("^(M{0,3})(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$", flags=2)
    ordinal_map: Dict[str, str] = {}
    path = resource_filename("zemberek", "resources/turkish-ordinal-numbers.txt")
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            key, value = line.split(':')
            ordinal_map[key] = value

    @staticmethod
    def roman_to_decimal(s: str) -> int:
        if s and len(s) > 0 and TurkishNumbers.roman_numeral_pattern.match(s):
            matcher = re.compile("M|CM|D|CD|C|XC|L|XL|X|IX|V|IV|I").match(s)
            decimal_values: Tuple = (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1)
            roman_numerals: Tuple = ("M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I")

            result = 0
            for gr in matcher.groups():
                for i, n in enumerate(roman_numerals):
                    if n == gr:
                        result += decimal_values[i]

            return result
        else:
            return -1

    @staticmethod
    def separate_numbers(s: str) -> List[str]:
        return TurkishNumbers.NUMBER_SEPARATION.findall(s)

    @staticmethod
    def convert_number_to_string(inp: str) -> str:
        if inp.startswith("+"):
            inp = inp[1:]

        sb: List[str] = []

        i = 0
        while i < len(inp) and inp[i] == 0:
            sb.append("sıfır")
            i += 1

        rest = inp[i:]
        if len(rest) > 0:
            sb.append(TurkishNumbers.convert_to_string(int(rest)))

        return " ".join(sb)

    @staticmethod
    def convert_to_string(inp: int) -> str:
        if inp == 0:
            return "sıfır"
        elif -999999999999999999 <= inp <= 999999999999999999:
            result = ""
            giris_pos = abs(inp)
            sayac = 0
            while giris_pos > 0:
                uclu = giris_pos % 1000
                if uclu != 0:
                    if uclu == 1 and sayac == 1:
                        result = f"{TurkishNumbers.thousands[sayac]} {result}"
                    else:
                        result = f"{TurkishNumbers.convert_three_digits(uclu)} {TurkishNumbers.thousands[sayac]}" \
                                 f" {result}"
                sayac += 1
                giris_pos /= 1000

            if inp < 0:
                return f"eksi {result.strip()}"
            else:
                return result.strip()
        else:
            raise ValueError("Number is out of bounds:" + str(inp))

    @staticmethod
    def convert_three_digits(three_digit_number: int) -> str:
        sonuc = ""
        hundreds = three_digit_number // 100
        tens = three_digit_number // 10 % 10
        single_digit = three_digit_number % 10
        if hundreds != 0:
            sonuc = "yüz"

        if hundreds > 1:
            sonuc = f"{TurkishNumbers.single_digit_numbers[hundreds]} {sonuc}"

        sonuc = f"{sonuc} {TurkishNumbers.ten_to_ninety[tens]} {TurkishNumbers.single_digit_numbers[single_digit]}"
        return sonuc.strip()
