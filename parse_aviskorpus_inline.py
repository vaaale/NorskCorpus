from bs4 import BeautifulSoup
import re
import tarfile
import zipfile
import io
import gzip
import argparse

AVIS_CORPUS_PATH = "/home/alex/Datasets/Norsk/norsk_aviskorpus.zip"
OUT_FILE = "avis-output.txt"


def argparse_setup():
    """Return arguments to pass to main.py from CLI."""
    parser = argparse.ArgumentParser(
        description="Make predictions using trained CatBoost model"
    )
    parser.add_argument(
        "--input",
        action="store",
        dest="input",
        default=AVIS_CORPUS_PATH,
        help="Path to zip archive",
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


def sub3_handler(archive, outpath):
    targz_buf = gzip.decompress(archive.read())
    buf = io.BytesIO(targz_buf)
    targz = tarfile.open(fileobj=buf)

    members = [member for member in targz.getmembers() if member.isfile() and '/nno/' not in member.name]
    sentences = []
    for member in members:
        f = targz.extractfile(member)
        doc = f.read().decode('iso8859-1')
        bs = BeautifulSoup(doc, 'lxml')
        text_div = bs.find("div", {"type": "text"})
        text = [p.getText() for p in text_div.find_all('p')]

        sentence = []
        for line in text:
            for word in line.split():
                if '.' == word or word.endswith('.'):
                    sentence.append(word)
                    sentences.append(" ".join(sentence))
                    sentence = []
                else:
                    sentence.append(word)
        with open(outpath, 'a') as out:
            out.writelines(f"{sentence}\n" for sentence in sentences)
            out.flush()
        print('Archive complete.')


def sub2_handler(archive, outpath):
    targz_buf = gzip.decompress(archive.read())
    buf = io.BytesIO(targz_buf)
    targz = tarfile.open(fileobj=buf)

    members = [member for member in targz.getmembers() if member.isfile()]
    sentences = []
    for member in members:
        f = targz.extractfile(member)
        data = f.read().decode('iso8859-1')
        lines = [line for line in data.split('\n') if not line.startswith("##")]
        sentence = []
        for line in lines:
            for word in line.split():
                if '.' == word or word.endswith('.'):
                    # sentence.append(word)
                    sentences.append(" ".join(sentence))
                    sentence = []
                else:
                    sentence.append(word)

        with open(outpath, 'a') as out:
            out.writelines(f"{sentence}\n" for sentence in sentences)
            out.flush()
        print('Archive complete.')


def sub1_handler(archive, outpath):
    lines = gzip.decompress(archive.read()).decode("iso8859-1").split("\n")
    sentences = []
    sentence = []
    for word in lines:
        word = re.sub('\n', '', word)
        if len(word) == 0 or word[0] in ['<', '|'] or "." == word and len(sentence) == 0:
            continue
        if "." == word and sentence[-1].lower() != 'nr':
            sentence.append(word)
            sentences.append(' '.join(sentence))
            sentence = []
        else:
            sentence.append(word)
    with open(outpath, 'a') as out:
        out.writelines(f"{sentence}\n" for sentence in sentences)
        out.flush()
    print('Archive complete.')


def process_avis_corpus(input, output):
    with zipfile.ZipFile(input, 'r') as aviszip:
        filelist = aviszip.filelist
        for fileinfo in filelist:
            if fileinfo.is_dir():
                continue
            print(f'Processing {fileinfo.name}....')
            archive = aviszip.open(fileinfo)
            if archive.name.startswith('1'):
                sub1_handler(archive, output)
            elif archive.name.startswith('2'):
                sub2_handler(archive, output)
            elif archive.name.startswith('3'):
                sub3_handler(archive, output)


if __name__ == '__main__':
    args = argparse_setup()
    process_avis_corpus(args.input, args.output)
    from git import Repo
    Repo.clone('https://github.com/attardi/wikiextractor.git')