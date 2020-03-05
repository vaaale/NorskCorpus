from bs4 import BeautifulSoup
import re
import tarfile
import zipfile
import io
import gzip
import os

from process_wikipedia import process_wikipedia
from utils import download_from_url

AVIS_CORPUS_URL = "http://www.nb.no/sbfil/tekst/norsk_aviskorpus.zip"
AVIS_CORSPUS_ARCHIVE = "norsk_aviskorpus.zip"


def _sub3_handler(archive, outpath):
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


def _sub2_handler(archive, outpath):
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


def _sub1_handler(archive, outpath):
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

def _maybe_download_norsk_aviskorpus(inputpath):
    archive_path = os.path.join(inputpath, AVIS_CORSPUS_ARCHIVE)
    if not os.path.isfile(archive_path):
        download_from_url(AVIS_CORPUS_URL, archive_path)


def process_avis_corpus(input, output):
    _maybe_download_norsk_aviskorpus(input)
    archive_path = os.path.join(input, AVIS_CORSPUS_ARCHIVE)

    with zipfile.ZipFile(archive_path, 'r') as aviszip:
        filelist = aviszip.filelist
        for fileinfo in filelist:
            if fileinfo.is_dir():
                continue
            print(f'Processing {fileinfo.filename}....')
            archive = aviszip.open(fileinfo)
            if archive.name.startswith('1'):
                _sub1_handler(archive, output)
            elif archive.name.startswith('2'):
                _sub2_handler(archive, output)
            elif archive.name.startswith('3'):
                _sub3_handler(archive, output)






