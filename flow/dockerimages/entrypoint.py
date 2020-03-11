from subprocess import Popen, PIPE
import sys
import json
import os

if __name__ == '__main__':
    args = sys.argv
    args[0] = "python3"
    print(args)
    process = Popen(args, stdout=PIPE, stderr=PIPE)

    if not os.path.isdir("../logs"):
        os.makedirs("../logs")

    with open("../logs/stdout.log", "w") as stdout, open("../logs/stderr.log", "w") as stderr:
        while True:
            stdout_lines = process.stdout.readlines()
            stderr_lines = process.stderr.readlines()

            if stdout_lines:
                for stdout_line in stdout_lines:
                    json_dict = {"source": "STDOUT", "message": stdout_line.decode('UTF-8').rstrip()}
                    message = json.dumps(json_dict)
                    stdout.write(message)
                    print(message)

            if stderr_lines:
                for stderr_line in stderr_lines:
                    json_dict = {"source": "STDERR", "message": stderr_line.decode('UTF-8').rstrip()}
                    message = json.dumps(json_dict)
                    stderr.write(message)
                    print(message)

            rc = process.poll()
            if rc:
                print(f"Process finished with code: {rc}")
                exit(rc)
