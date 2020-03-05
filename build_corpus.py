import argparse
import os

from process_avis_corpus import process_avis_corpus
from process_wikipedia import process_wikipedia


OUT_FILE = "norsk_corpus.txt"


def argparse_setup():
    """Return arguments to pass to main.py from CLI."""
    parser = argparse.ArgumentParser(
        description="Make predictions using trained CatBoost model"
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

    process_avis_corpus(args.input, args.output)
    process_wikipedia(args.input, args.output)

