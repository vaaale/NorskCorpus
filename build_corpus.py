import argparse
import os

from parse_xml_books import process_books
from process_avis_corpus import process_avis_corpus
from process_wikipedia import process_wikipedia


OUT_FILE = "norsk_corpus.txt"


def argparse_setup():
    """Return arguments to pass to main.py from CLI."""
    parser = argparse.ArgumentParser(
        description="Build Norwegian corpus."
    )
    parser.add_argument(
        "--input",
        action="store",
        dest="input",
        default="./data",
        help="Path data",
    )
    parser.add_argument(
        "--output",
        action="store",
        dest="output",
        default=OUT_FILE,
        help="Path to output data",
    )
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    args = argparse_setup()
    if not os.path.isdir(args.input):
        os.makedirs(args.input)
    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    output = os.path.join(args.output, "norsk_korpus.txt")
    process_avis_corpus(args.input, output, workers=2)
    process_wikipedia(args.input, output)
    process_books(args.input, output)
    print("This is an OK message from build_corpus.py")
    raise Exception("Something went very wrong!!")

