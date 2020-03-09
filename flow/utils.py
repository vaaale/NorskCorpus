import os


def sftp_exists(sftp, path):
    try:
        sftp.stat(path)
        return True
    except FileNotFoundError:
        return False


def gather_files(path):
    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        if ".idea" in r or ".venv" in r:
            continue
        for file in f:
            if '.py' in file:
                files.append(os.path.join(r, file))
    if os.path.exists(os.path.join(path, "requirements.txt")):
        files.append(os.path.join(path, "requirements.txt"))
    return files


