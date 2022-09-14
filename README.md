# ZEMBEREK-PYTHON

Python implementation of Natural Language Processing library 
for Turkish, [zemberek-nlp](https://github.com/ahmetaa/zemberek-nlp). It is based on
zemberek 0.17.1 and is completely written in Python meaning there is no need to setup
a Java development environment to run it.

*Source Code*

https://github.com/Loodos/zemberek-python

**Dependencies**
* antlr4-python3-runtime==4.8
* numpy>=1.19.0

## Supported Modules
Currently, following modules are supported.

* Core (Partially)
    
* TurkishMorphology (Partially)
    * Single Word Analysis
    * Diacritics Ignored Analysis
    * Word Generation
    * Sentence Analysis
    * Ambiguity Resolution
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

In [MultiLevelMphf](zemberek/core/hash/multi_level_mphf.py) class, in the original Java
implementation, there are some integer multiplication operations which I
tried to reimplement using vanilla Python 'int', but the results were not the
same. Then I tried it with numpy.int32 and numpy.float32, since default java
int and float types are 4 byte. The results were the same with Java, however, oftenly
these operations produced RuntimeWarning as the multiplication caused overflow. In Java 
there were no overflow warnings whatsoever. I could not find a reasonable explanation to
this situation, nor I could find a better way to implement it. So I suppressed overflow warnings
for MultiLevelMphf. Therefore, please be aware that, this is not a healthy behaviour, and you should 
be careful using this code.



## Credits
This project is Python port of [zemberek-nlp](https://github.com/ahmetaa/zemberek-nlp). 

