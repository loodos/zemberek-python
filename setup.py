import setuptools

setuptools.setup(
    name='zemberek',
    version='0.1.0',
    author='Loodos Tech',
    description='Python implementation of open source text processing library for Turkish, zemberek',
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={
      '': ["zemberek/resources/*.txt",
           "zemberek/resources/*.csv",
           "zemberek/resources/*.slm",
           "zemberek/resources/*.pickle"]
    },
    url='https://gitlab.com/loodos/inhouse/marvin/lds-marvin-zemberek-python.git',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.7',
    install_requires=[
        'antlr4-python3-runtime>=4.8',
        'numpy>=1.18.2'
    ],
    py_modules=['zemberek'],
)
