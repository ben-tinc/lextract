#!/usr/bin/env python3
#
from os import path, walk

from lxml import etree
import nltk
# import spacy # nltk suffices atm

###############################################################################
# Configuration

EDITED_DIR = path.join(".", "edited")
SOURCE_DIR = path.join(".", "xml")
PLAIN_DIR = path.join(".", "plaintext")
TARGET_DIR = path.join(".", "reference")

GROUPS = ['zufall', 'auswahl']
# GROUPS = ['one', ]

###############################################################################
# Strategy:
# nlp = spacy.load('de')

nltk.data.path.append(path.join(".", "nltk_data"))


def load_file(filepath):
    """Load XML source file with lxml and parse it into an etree"""
    # print("load source file")
    with open(filepath, "r") as f:
        tree = etree.parse(f)
    return tree


def write_plain_text(tree, group, filename):
    """Take any xml file, get its text tag and write its plaintext
    content into a corresponding file in the PLAIN_DIR.
    """
    filepath = path.join(PLAIN_DIR, group, filename + ".txt")
    el = tree.getroot().find("text")
    with open(filepath, "w") as f:
        f.write(etree.tostring(el, method="text", encoding="unicode"))


def preprocess_xml(tree):
    """Preprocess an etree to make it suitable for tokenization."""
    text = tree.getroot().find("text")
    for p in text.iter("note", "lb"):
        if(p.tag == "note"):
            # insert whitespace into every <note>
            try:
                p.text = " " + p.text
            except TypeError:
                # If p.text is None, because it immediately contains another tag,
                # just insert a single space character.
                p.text = " "
        else:
            # insert whitespace after every <lb/>
            try:
                p.tail = " " + p.tail
            except TypeError:
                p.tail = " "
    return tree


def write_edited(tree, group, filename):
    """Write an etree to an xml file in the EDITED_DIR."""
    filepath = path.join(EDITED_DIR, group, filename)
    tree.write(filepath)


def extract_ps(root):
    """Extract all the paragraphs and store them in a list"""
    ps = []
    text = root.find("text")
    for p in text.iter("p"):
        s = etree.tostring(p, method="text", encoding="unicode")
        ps.append(tokenize_p(s))
    return ps


def tokenize_p(p):
    """Tokenize each Paragraph with nltk."""
    tokenizer = nltk.data.load("tokenizers/punkt/german.pickle")
    sents = tokenizer.tokenize(p)
    tokens = []
    for s in sents:
        tokens.extend(nltk.tokenize.word_tokenize(s))
    tokens = [
        t.strip() for t in tokens
        if not (t.strip().isspace() or t.strip() in [",", ".", ";", "!", "?", "-", '"', "'", "``", "''", ":", "(", ")"])
    ]
    return tokens


def write_reference(ps, group, filename):
    with open(path.join(TARGET_DIR, group, filename + ".txt"), "w") as f:
        for stuff in ps:
            for idx, s in enumerate(stuff):
                if idx != 0:
                    f.write(" ")
                f.write(str(s) + "(" + str(idx) + ")")
            f.write("\n\n")


if __name__ == "__main__":
    # Check both directories in SOURCE_DIR
    for group in GROUPS:
        # Grab all files in SOURCE_DIR
        files = []
        for (dirpath, dirnames, filenames) in walk(path.join(SOURCE_DIR, group)):
            files.extend(filenames)
            # only toplevel files needed
            break
        # Read all files
        for filename in files:
            # Parse XML
            tree = load_file(path.join(SOURCE_DIR, group, filename))
            # Preprocess XML
            tree = preprocess_xml(tree)
            # Write plaintext file
            write_plain_text(tree, group, filename)
            # Write intermediate XML file
            write_edited(tree, group, filename)
            # Parse edited XML
            tree = load_file(path.join(EDITED_DIR, group, filename))
            ps = extract_ps(tree)

            # Write reference file to TARGET_DIR
            if ps is not None:
                write_reference(ps, group, filename)
