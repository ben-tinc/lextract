#!/usr/bin/env python3
#
import argparse
from os import path, walk

from lxml import etree
import nltk
# import spacy # not neccessary, nltk suffices atm

###############################################################################
# Configuration

MOD_DIR = path.join(".", "edited")
SOURCE_DIR = path.join(".", "source")
PLAIN_DIR = path.join(".", "plaintext")
REF_DIR = path.join(".", "reference")
XML_DIR = path.join(".", "results")

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


def fix_whitespace(tree):
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


def remove_notes(tree):
    for note in tree.getroot().iter("note"):
        parent = note.getparent()
        parent.text += note.tail
        parent.remove(note)
    return tree


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
        if not (t.strip().isspace() or t.strip() in [",", ".", ";", "!", "?",
                "-", '"', "'", "``", "''", ":", "(", ")"])
    ]
    return tokens


def write_edited(tree, filepath):
    """Write an etree to an xml file in the MOD_DIR."""
    tree.write(filepath)


def write_reference(ps, filename):
    with open(path.join(filename), "w") as f:
        for stuff in ps:
            for idx, s in enumerate(stuff):
                if idx != 0:
                    f.write(" ")
                f.write(str(s) + "(" + str(idx) + ")")
            f.write("\n\n")


def write_plain_text(tree, filename):
    """Take any xml file, get its text tag and write its plaintext
    content into a corresponding file in the PLAIN_DIR.
    """
    filepath = path.join(filename)
    el = tree.getroot().find("text")
    with open(filepath, "w") as f:
        f.write(etree.tostring(el, method="text", encoding="unicode"))


def write_xml(ps, tree, filename):
    raise NotImplementedError("")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="directory with source xml files")
    # Flags wether preprocess and to write certain files
    parser.add_argument(
        "-n", "--no-notes", action="store_true",
        help="exclude all <note> tags from the source files")
    parser.add_argument(
        "-f", "--fix-whitespace", action="store_true",
        help="preprocess the xml before tokenization")
    parser.add_argument(
        "-r", "--write-reference", action="store_true",
        help="write reference text files")
    parser.add_argument(
        "-e", "--write-edited", action="store_true",
        help="write preprocessed xml into a file")
    parser.add_argument(
        "-p", "--write-plaintext", action="store_true",
        help="write plaintext files")
    parser.add_argument(
        "-x", "--write-xml", action="store_true",
        help="write tokenized xml files")

    # Location where to write files
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
        "write_ref": args.write_reference or bool(args.ref_dir),
        "write_plain": args.write_plaintext or bool(args.plain_dir),
        "write_xml": args.write_xml or bool(args.xml_dir),
        "src_dir": args.source,
        "mod_dir": args.mod_dir or MOD_DIR,
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

        if opts["mod_dir"] or opts["write_edited"]:
            write_edited(tree, path.join(opts["mod_dir"], filename))

        # Processing and output generation
        paragraphs = None
        # Do we actually need to tokenize?
        if opts["write_ref"] or opts["write_xml"]:
            paragraphs = extract_ps(tree)

        if opts["write_plain"]:
            write_plain_text(tree, path.join(opts["plain_dir"], filename + ".txt"))

        if opts["write_ref"] and paragraphs is not None:
            write_reference(paragraphs, path.join(opts["ref_dir"], filename + ".txt"))

        if opts["write_xml"] and paragraphs is not None:
            write_xml(tree, paragraphs, path.join(opts["xml_dir"], filename))
