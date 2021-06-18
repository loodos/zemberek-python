# ZEMBEREK-PYTHON

Python implementation of Natural Language Processing library 
for Turkish, [zemberek-nlp](https://github.com/ahmetaa/zemberek-nlp). It is based on
zemberek 0.17.1 and is completely written in Python meaning there is no need to setup
a Java development environment to run it.

*Source Code*

https://github.com/Loodos/zemberek-python

**Dependencies**
* antlr4-python3-runtime>=4.8
* numpy>=1.19.0

## Supported Modules
Currently, following modules are supported.

* Core (Partially)
    
* TurkishMorphology (Partially)
    * Single Word Analysis
    * Diacritics Ignored Analysis
    * Word Generation
* Tokenization
    * Sentence Boundary Detection
    * Tokenization
* Normalization (Partially)
    * Spelling Suggestion
    * Noisy Text Normalization

## Installation
You can install the package with pip

    pip install zemberek-python

## Examples
Example usages can be found in [examples.py](zemberek/examples.py)

## Notes
There are some minor changes in codes where original contains some Java specific
functionality and data structures. We used Python 
equivalents as much as we could but sometimes we needed to change them. And it
affects the performance and accuracy a bit.


## Credits
This project is Python port of [zemberek-nlp](https://github.com/ahmetaa/zemberek-nlp). 

