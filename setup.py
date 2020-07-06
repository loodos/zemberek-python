import setuptools

setuptools.setup(
    name='zemberek',
    version='0.0.1',
    author='Loodos Tech',
    description='Python implementation of open source text processing library zemberek',
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={
      '': ["zemberek/resources/*.txt",
           "zemberek/resources/*.csv",
           "zemberek/resources/*.slm"]
    },
    url='git@gitlab.com:harun.uz/zemberek.git',
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
