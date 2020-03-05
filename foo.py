import tarfile
from multiprocessing.pool import Pool

from bs4 import BeautifulSoup
import os
from tqdm import tqdm

PATH = "/home/alex/Datasets/Norsk/boker"


def parse_doc(doc):
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
                sentences.append(text_line)
                # print(text_line)
                sentence = []
            else:
                sentence.append(content)
    return sentences


def process_member(archive):
    tar = tarfile.open(archive, "r:gz")
    document = []
    for member in tar.getmembers():
        f = tar.extractfile(member)
        if f is not None:
            xml_doc = f.read()
            sentences = parse_doc(xml_doc)
            document.append(sentences)
    return document


if __name__ == '__main__':
    files = [os.path.join(PATH, file) for file in os.listdir(PATH)]
    with Pool(6) as p:
        documents = tqdm(p.imap_unordered(process_member, files, chunksize=1), total=len(files))
        for doc in documents:
            with open('output.txt', 'a') as out:
                for sentences in doc:
                    out.writelines(f"{sentence}\n" for sentence in sentences)
                out.flush()



