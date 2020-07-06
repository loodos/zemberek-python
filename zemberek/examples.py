import os
os.chdir("../")

from zemberek import TurkishSpellChecker, TurkishSentenceNormalizer
from zemberek import TurkishSentenceExtractor
from zemberek import TurkishMorphology

"""
examples = [#"Yrn okua gidicem",
            "Tmm, yarin havuza giricem ve aksama kadar yaticam :)",
            "ah aynen ya annemde fark ettı siz evinizden cıkmayın diyo",
            "gercek mı bu? Yuh! Artık unutulması bile beklenmiyo",
            "Hayır hayat telaşm olmasa alacam buraları gökdelen dikicem.",
            "yok hocam kesınlıkle oyle birşey yok",
            "herseyi soyle hayatında olmaması gerek bence boyle ınsanların falan baskı yapıyosa"]
"""
examples = ["Kıredi taksitm ne kadr kaldı?",
            "Kredi başvrusu yapmk istiyrum.",
            "Bankanizin hesp blgilerini ogrenmek istyorum."]

mor = TurkishMorphology.create_with_defaults()

normalizer = TurkishSentenceNormalizer(mor)

for example in examples:
    print(example)
    print(normalizer.normalize(example), "\n")


sc = TurkishSpellChecker(mor)

li = ["okuyablirim", "tartısıyor", "Ankar'ada", "knlıca"]
for word in li:
    print(word + " = " + ' '.join(sc.suggest_for_word(word)))
"""

"""
extractor = TurkishSentenceExtractor()

text = "İstanbul'da Boğaziçi ve Fatih Sultan Mehmet adlarında iki köprü vardır. "

sentences = extractor.from_paragraph(text)

for sentence in sentences:
    print(sentence)

