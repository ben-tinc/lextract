# tokenizer.py


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

Afterwards download the german language data for nltk to a folder 'nltk_data'
in the directory, where tokenizer.py resides. 


## Basic Usage

You can start it on the console like this:

```
python3 tokenizer.py
```

View its usage notes by specifying the --help parameter:

```
python3 tokenizer.py --help
```