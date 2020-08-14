import time
import logging

from zemberek import (
    TurkishSpellChecker,
    TurkishSentenceNormalizer,
    TurkishSentenceExtractor,
    TurkishMorphology,
    TurkishTokenizer
)

logger = logging.getLogger(__name__)

examples = ["Yrn okua gidicem",
            "Tmm, yarin havuza giricem ve aksama kadar yaticam :)",
            "ah aynen ya annemde fark ettı siz evinizden cıkmayın diyo",
            "gercek mı bu? Yuh! Artık unutulması bile beklenmiyo",
            "Hayır hayat telaşm olmasa alacam buraları gökdelen dikicem.",
            "yok hocam kesınlıkle oyle birşey yok",
            "herseyi soyle hayatında olmaması gerek bence boyle ınsanların falan baskı yapıyosa",
            "email adresim zemberek_python@loodos.com",
            "Kredi başvrusu yapmk istiyrum.",
            "Bankanizin hesp blgilerini ogrenmek istyorum."]

morphology = TurkishMorphology.create_with_defaults()

# SENTENCE NORMALIZATION
start = time.time()
normalizer = TurkishSentenceNormalizer(morphology)
logger.info(f"Normalization instance created in: {time.time() - start} s")

start = time.time()
for example in examples:
    print(example)
    print(normalizer.normalize(example), "\n")
logger.info(f"Sentences normalized in: {time.time() - start} s")

start = time.time()
sc = TurkishSpellChecker(morphology)
logger.info(f"Spell checker instance created in: {time.time() - start} s")


# SPELLING SUGGESTION
li = ["okuyablirim", "tartısıyor", "Ankar'ada", "knlıca", "yapablrim", "kıredi", "geldm", "geliyom", "aldm", "asln"]
start = time.time()
for word in li:
    print(word + " = " + ' '.join(sc.suggest_for_word(word)))
logger.info(f"Spells checked in: {time.time() - start} s")


# SENTENCE BOUNDARY DETECTION
start = time.time()
extractor = TurkishSentenceExtractor()
print("Extractor instance created in: ", time.time() - start, " s")

text = "İnsanoğlu aslında ne para ne sevgi ne kariyer ne şöhret ne de çevre ile sonsuza dek mutlu olabilecek bir " \
       "yapıya sahiptir. Dış kaynaklardan gelebilecek bu mutluluklar sadece belirli bir zaman için insanı mutlu " \
       "kılıyor. Kişi bu kaynakları elde ettiği zaman belirli bir dönem için kendini iyi hissediyor, ancak alışma " \
       "dönemine girdiği andan itibaren bu iyilik hali hızla tükeniyor. Mutlu olma sanatının özü bu değildir. Gerçek " \
       "mutluluk, kişinin her türlü olaya ve duruma karşı kendini pozitif tutarak mutlu hissedebilmesi halidir. Bu " \
       "davranış şeklini edinen insan, zor günlerde güçlü, mutlu günlerde zevk alan biri olur ve mutluluğu kalıcı " \
       "kılar. "

start = time.time()
sentences = extractor.from_paragraph(text)
print(f"Sentences separated in {time.time() - start}s")

for sentence in sentences:
    print(sentence)
print("\n")

# SINGLE WORD MORPHOLOGICAL ANALYSIS
results = morphology.analyze("kalemin")
for result in results:
    print(result)
print("\n")

# TOKENIZATION
tokenizer = TurkishTokenizer.DEFAULT

tokens = tokenizer.tokenize("Saat 12:00.")
for token in tokens:
    print('Content = ', token.content)
    print('Type = ', token.type_.name)
    print('Start = ', token.start)
    print('Stop = ', token.end, '\n')
