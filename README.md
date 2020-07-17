Python implementation of Natural Language Processing library 
for Turkish, [zemberek](https://github.com/ahmetaa/zemberek-nlp).

Only project members can install this package via 
_pip install git+ssh://git@gitlab.com/loodos/inhouse/marvin/lds-marvin-zemberek-python.git_

**Dependencies**
* antlr4-python3-runtime==4.8
* numpy==1.18.2

Example usages can be found in examples.py

There are some minor changes in codes where original contains some Java specific
functionality and data structures. For data structures we used Python 
equivalents as much as we could but sometimes we needed to change them. And it
affects the performance and accuracy a bit.

Many optimization can be made, further versions will be 
released mostly on optimization.
