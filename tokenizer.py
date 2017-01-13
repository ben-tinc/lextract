#!/usr/bin/env python3
#
#    tokenizer.py -- A small script to (pre-)process TEI XML files
#
#    Copyright (c) 2017 Henning Gebhard
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
from os import path, walk

from lxml import etree
import nltk
from nltk.stem.snowball import SnowballStemmer

###############################################################################
# Configuration

PROJECT_DIR = path.dirname(path.abspath(__file__))
NLTK_DIR = path.join(PROJECT_DIR, "nltk_data")
MOD_DIR = path.join(PROJECT_DIR, "edited")
SOURCE_DIR = path.join(PROJECT_DIR, "source")
PLAIN_DIR = path.join(PROJECT_DIR, "plaintext")
REF_DIR = path.join(PROJECT_DIR, "reference")
STE_DIR = path.join(PROJECT_DIR, "stemmed")
XML_DIR = path.join(PROJECT_DIR, "results")


###############################################################################

"""
tokenizer.py

A library as well as a script to (pre-)process TEI XML files. It mainly
provides tokenization and text extraction, but it can also fix some
common whitespace problems before that.

It is tailored specifically to the needs of the course "Praxis der DH"
and I doubt that it is very useful for anything else without at least
some custom modifications.
"""

nltk.data.path.append(NLTK_DIR)


def load_file(filepath):
    """Load XML source file with lxml and parse it into an etree."""
    with open(filepath, "r") as f:
        tree = etree.parse(f)
    return tree


def fix_whitespace(tree):
    """Fix some common whitespace problems to make it suitable
    for tokenization.
    """
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


def remove_notes(tree):
    """Exclude all <note> tags from the tree."""
    for note in tree.getroot().iter("note"):
        parent = note.getparent()
        try:
            parent.text += note.tail
        except TypeError:
            pass
        finally:
            parent.remove(note)
    return tree


def extract_ps(root):
    """Extract all the paragraphs from the tree and return its
    text content as a list of tokenized strings."""
    ps = []
    text = root.find("text")
    for p in text.iter("p"):
        s = etree.tostring(p, method="text", encoding="unicode")
        ps.append(tokenize_paragraph(s))
    return ps


def tokenize_paragraph(p):
    """Tokenize a Paragraph with nltk and remove redundant whitespace.
    'Tokens' which end up being only punctuation are also removed."""
    tokenizer = nltk.data.load("tokenizers/punkt/german.pickle")
    sentences = tokenizer.tokenize(p)
    tokens = []
    for s in sentences:
        tokens.extend(nltk.tokenize.word_tokenize(s))
    tokens = [
        t.strip() for t in tokens
        if not (t.strip().isspace() or t.strip() in [",", ".", ";", "!", "?",
                "-", '"', "'", "``", "''", ":", "(", ")", "–"])
    ]
    return tokens


def write_reference(ps, filename):
    """Write a plain text file with one line per paragraph
    and a index number in parentheses after each token.
    """
    with open(path.join(filename), "w") as f:
        for stuff in ps:
            for idx, s in enumerate(stuff):
                if idx != 0:
                    f.write(" ")
                f.write(str(s) + "(" + str(idx) + ")")
            f.write("\n\n")


def write_plain_text(tree, filepath):
    """Take any xml file, get its text tag and write its plaintext
    content into a corresponding file in the PLAIN_DIR.
    """
    el = tree.getroot().find("text")
    with open(filepath, "w") as f:
        f.write(etree.tostring(el, method="text", encoding="unicode"))


def write_stemmed_plain_text(tree, filename):
    """Write a plain text file, with each token of the text replaced
    by its stemmed version
    """
    stemmer = SnowballStemmer("german")
    plaintext = etree.tostring(
        tree.getroot().find("text"),
        method="text", enocding="utf-8"
    )
    raise NotImplementedError("")


def write_xml(ps, tree, filename):
    """Wrap every token of the tree in a <w> tag and write the result
    into a new file.
    """
    raise NotImplementedError("")


# This is executed when the script is called directly via `python3 tokenizer.py`.
if __name__ == "__main__":

    # Process all the command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="directory with source xml files")
    parser.add_argument(
        "-n", "--no-notes", action="store_true",
        help="exclude all <note> tags from the source files")
    parser.add_argument(
        "-f", "--fix-whitespace", action="store_true",
        help="preprocess the xml before tokenization")
    parser.add_argument(
        "-s", "--use-stemming", action="store_true",
        help="use stemming on plaintext")
    parser.add_argument(
        "-r", "--write-reference", action="store_true",
        help="write reference text files")
    parser.add_argument(
        "-m", "--write-modified", action="store_true",
        help="write preprocessed xml into a file")
    parser.add_argument(
        "-p", "--write-plaintext", action="store_true",
        help="write plaintext files")
    parser.add_argument(
        "-x", "--write-xml", action="store_true",
        help="write tokenized xml files")

    # Location where to write files
    parser.add_argument(
        "--stemm-dir", help="where to write stemmed plain text files. Implies -s option.")
    parser.add_argument(
        "--mod-dir",
        help="where to create intermediate xml files with fixed whitespace. Implies -f option.")
    parser.add_argument(
        "--ref-dir", help="where to create reference files. Implies -r option.")
    parser.add_argument(
        "--plain-dir", help="where to create plaintext files. Implies -p option.")
    parser.add_argument(
        "--xml-dir", help="where to create tokenized xml files. Implies -x option.")

    args = parser.parse_args()

    opts = {
        "no_notes": args.no_notes,
        "fix_whitespace": args.fix_whitespace,
        "write_stemm": args.use_stemming or bool(args.stemm_dir),
        "write_ref": args.write_reference or bool(args.ref_dir),
        "write_plain": args.write_plaintext or bool(args.plain_dir),
        "write_xml": args.write_xml or bool(args.xml_dir),
        "src_dir": args.source,
        "mod_dir": args.mod_dir or MOD_DIR,
        "ste_dir": args.stemm_dir or STE_DIR,
        "ref_dir": args.ref_dir or REF_DIR,
        "xml_dir": args.xml_dir or XML_DIR,
        "plain_dir": args.plain_dir or PLAIN_DIR,
    }

    # Determine files to process.
    files = []
    filepath = None
    for (dirpath, dirnames, filenames) in walk(path.join(opts["src_dir"])):
        files.extend(filenames)
        filepath = dirpath
        break

    # Process files.
    for filename in files:
        tree = None
        tree = load_file(path.join(filepath, filename))

        # Preprocessing steps
        if opts["no_notes"]:
            tree = remove_notes(tree)
        if opts["fix_whitespace"]:
            tree = fix_whitespace(tree)

        if opts["mod_dir"] or opts["write_modified"]:
            tree.write(path.join(opts["mod_dir"], filename))

        # Processing and output generation
        paragraphs = None
        # Do we actually need to tokenize?
        if opts["write_ref"] or opts["write_xml"]:
            paragraphs = extract_ps(tree)

        if opts["write_plain"]:
            write_plain_text(tree, path.join(opts["plain_dir"], filename + ".txt"))

        if opts["write_stemm"]:
            write_stemmed_plain_text(tree, path.join(opts["ste_dir"], filename + ".txt"))

        if opts["write_ref"] and paragraphs is not None:
            write_reference(paragraphs, path.join(opts["ref_dir"], filename + ".txt"),
                            opts["stemming"])

        if opts["write_xml"] and paragraphs is not None:
            write_xml(tree, paragraphs, path.join(opts["xml_dir"], filename))
