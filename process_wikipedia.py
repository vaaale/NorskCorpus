import os

from utils import execute, download_from_url

WIKI_DUMP_NAME = "nowiki-latest-pages-articles.xml.bz2"


def _maybe_download_wikipedia(inputpath):
    wiki_dump_url = f"https://dumps.wikimedia.org/nowiki/latest/{WIKI_DUMP_NAME}"
    archive_path = os.path.join(inputpath, WIKI_DUMP_NAME)
    if not os.path.isfile(archive_path):
        download_from_url(wiki_dump_url, archive_path)


def _wikipedia(inputpath, output):
    archive_path = os.path.join(inputpath, WIKI_DUMP_NAME)

    program_vector = ['python', "wikiextractor/WikiExtractor.py", archive_path, "--processes", "8", "-q", "-o",  "-" ]
    execute(program_vector, output)


def process_wikipedia(datadir, outputpath):
    _maybe_download_wikipedia(datadir)

    if not os.path.isdir('wikiextractor'):
        from git import Repo
        Repo.clone_from('https://github.com/attardi/wikiextractor.git', 'wikiextractor')
    _wikipedia(datadir, outputpath)
