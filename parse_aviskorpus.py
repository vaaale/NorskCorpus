from bs4 import BeautifulSoup
import os
import codecs
import re
import tarfile
import zipfile

AVIS_CORPUS_PATH = "/home/alex/Datasets/Norsk/norsk_aviskorpus.zip"

PATH = "/home/alex/Datasets/Norsk/avis"
SUB1 = os.path.join(PATH, "1")
SUB2 = os.path.join(PATH, "2")
SUB3 = os.path.join(PATH, "3")


def sub1_handler(outpath):
    files = os.listdir(SUB1)
    for file in files:
        sentences = []
        with codecs.open(os.path.join(SUB1, file), 'r', encoding='iso8859-1') as inp:
            sentence = []
            for word in inp:
                word = re.sub('\n', '', word)
                if len(word) == 0 or word[0] in ['<', '|'] or "." == word and len(sentence) == 0:
                    continue
                if "." == word and sentence[-1].lower() != 'nr':
                    sentence.append(word)
                    sentences.append(sentence)
                    sentence = []
                else:
                    sentence.append(word)
        with open(outpath, 'a') as out:
            out.writelines(f"{sentence}\n" for sentence in sentences)
            out.flush()
        print(f'{file}\nArchive complete.')


def _process_sub2_archive(archive):
    tar = tarfile.open(archive, "r:gz")
    members = [member for member in tar.getmembers() if member.isfile()]
    sentences = []
    for member in members:
        f = tar.extractfile(member)
        data = f.read().decode('iso8859-1')
        lines = [line for line in data.split('\n') if not line.startswith("##")]
        sentence = []
        for line in lines:
            for word in line.split():
                if '.' == word or word.endswith('.'):
                    sentence.append(word)
                    sentences.append(" ".join(sentence))
                    sentence = []
                else:
                    sentence.append(word)
    return sentences


def sub2_handler(outpath):
    files = os.listdir(SUB2)
    for file in files:
        filename = os.path.join(SUB2, file)
        if not os.path.isfile(filename):
            continue
        sentences = _process_sub2_archive(filename)
        with open(outpath, 'a') as out:
            out.writelines(f"{sentence}\n" for sentence in sentences)
            out.flush()
        print(f'{file}\nArchive complete.')


def _process_sub3_archive(archive):
    tar = tarfile.open(archive, "r:gz")
    members = [member for member in tar.getmembers() if member.isfile() and '/nno/' not in member.name]
    sentences = []
    for member in members:
        f = tar.extractfile(member)
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
    return sentences


def sub3_handler(outpath):
    files = os.listdir(SUB3)
    for file in files:
        filename = os.path.join(SUB3, file)
        if not os.path.isfile(filename):
            continue
        sentences = _process_sub3_archive(filename)
        with open(outpath, 'a') as out:
            out.writelines(f"{sentence}\n" for sentence in sentences)
            out.flush()
        print(f'{file}\nArchive complete.')


if __name__ == '__main__':
    sub1_handler('avis-output.txt')
    sub2_handler('avis-output.txt')
    sub3_handler('avis-output.txt')