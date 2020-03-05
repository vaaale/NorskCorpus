import subprocess
from urllib.request import urlopen

from tqdm import tqdm
import requests
import os


def download_from_url(url, dst):
    """
    @param: url to download file
    @param: dst place to put the file
    """
    file_size = int(urlopen(url).info().get('Content-Length', -1))
    if os.path.exists(dst):
        first_byte = os.path.getsize(dst)
    else:
        first_byte = 0
    if first_byte >= file_size:
        return file_size
    header = {"Range": "bytes=%s-%s" % (first_byte, file_size)}
    pbar = tqdm(total=file_size, initial=first_byte, unit='B', unit_scale=True, desc=url.split('/')[-1])
    req = requests.get(url, headers=header, stream=True)
    with(open(dst, 'ab')) as f:
        for chunk in req.iter_content(chunk_size=4096):
            if chunk:
                f.write(chunk)
                pbar.update(4096)
    pbar.close()
    return file_size


def execute(program_vector, output):
    process = subprocess.Popen(program_vector,
                               stdout=subprocess.PIPE,
                               universal_newlines=True)
    with open(output, 'a') as outfile:
        while True:
            return_code = process.poll()
            while True:
                line = process.stdout.readline()
                if len(line.strip()) > 0 and not line.startswith("<doc id=") and not line.startswith("</doc>"):
                    print(line.strip(), file=outfile)
                if not line:
                    break
            if return_code is not None:
                break
