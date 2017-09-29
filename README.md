# lextract.py


A script to automate (pre-) processing of the xml corpus for the course
"Praxis der DH". Features include: 

- whitespace fixes
- removal of <note> tags
- tokenization (save as reference txt or inside of xml)
- stemming
- extraction of document body as plain text


## Installation

Just download this script. Then install its dependencies nltk and lxml.
You can install these libraries via pip.

```
pip install lxml
pip install nltk
``` 

Afterwards download the german language data for nltk to a folder 'nltk_data/'
in the directory, where lextract.py resides. 


## Basic Usage

This script assumes that you have language data in the directory `./nltk_data/` and your source files a directory `./source/`.  You can start it on the console like this:

```
python3 lextract.py
```

Most directories used can be specified via parameters. 
View more detailed usage notes by specifying the --help parameter:

```
python3 lextract.py --help
```

Let's say, you have your source xml files in the directory ~/xml. You want to fix erroneous whitespace, remove note tags and write the files' content as plaintext into the directory ~/plaintext. You can achieve this by using

```
python3 lextract.py ~/xml -f -n --plain-dir ~/plaintext
```
