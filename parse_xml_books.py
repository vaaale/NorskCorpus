from io import BytesIO
from multiprocessing.pool import Pool
from bs4 import BeautifulSoup
import os
from tqdm import tqdm
from utils import download_from_url
import tarfile

BOOKS_DOWNLOAD_URL = "http://www.nb.no/sbfil/xml_boker_idf/xml_idf_boker_gz.tar"
BOOKS_ARCHIVE = "xml_idf_boker_gz.tar"


def _maybe_download(inputpath):
    archive_path = os.path.join(inputpath, BOOKS_ARCHIVE)
    if not os.path.isfile(archive_path):
        download_from_url(BOOKS_DOWNLOAD_URL, archive_path)


def _extract_text(doc):
    bs = BeautifulSoup(doc, 'lxml')
    textlines = bs.find_all('textline')
    sentences = []
    sentence = []
    for textline in textlines:
        strings = textline.find_all('string')
        for string in strings:
            content = string.get('content')
            if content.endswith('.'):
                sentence.append(content)
                text_line = " ".join(sentence)
                if not "." == text_line:
                    sentences.append(text_line)
                sentence = []
            else:
                sentence.append(content)
    return sentences


def _process_book(archive):
    tar = tarfile.open(fileobj=archive, mode="r:gz")
    chapters = [tar.extractfile(member) for member in tar.getmembers()]
    chapters = [c.read() for c in chapters if c]
    documents = []
    with Pool(6) as p:
        sentences = tqdm(p.imap_unordered(_extract_text, chapters, chunksize=1), total=len(chapters))
        for sentence in sentences:
            if len(sentence) > 0:
                documents.append(sentence)
    return documents


def process_books(input, output):
    _maybe_download(input)

    archive_name = os.path.join(input, BOOKS_ARCHIVE)
    tar = tarfile.open(archive_name, "r")

    books = tar.getmembers()
    for book in books:
        archive = tar.extractfile(book)
        if not archive:
            continue
        buf = BytesIO(archive.read())
        text = _process_book(buf)
        with open(output, 'a') as out:
            for sentences in text:
                for sentence in sentences:
                    out.writelines(f"{sentence}\n")
            out.flush()


if __name__ == '__main__':
    process_books("./data", "output.txt")





