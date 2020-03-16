import os
import paramiko
import tarfile
import docker
from io import BytesIO
import numpy as np
from flow.utils import gather_files, sftp_exists
import threading


class DataReference:
    def __init__(self, path):
        self.path = path

    def build(self, basepath, run_id):
        self.host_path = f"{basepath}/{run_id}/{self.path}"
        self.container_path = f"/{self.path}"

    def tear_down(self):
        pass

    def __str__(self) -> str:
        return self.container_path


class ComputeTarget:
    def __init__(self, server, username, password):
        self.password = password
        self.username = username
        self.server = server
        self.basepath = "/home/compute"
        self.rund_id = "default_run"
        self.exit_code = 0
        self.run_log = []

    def _make_tarfile(self, archive_name, source_dir):
        files = gather_files(source_dir)
        with tarfile.open(os.path.join(source_dir, archive_name), "w:gz") as tar:
            for file in files:
                _file = os.path.relpath(file, source_dir).replace('\\', '/')
                tar.add(file, _file)
            tar.close()

    def _init_workspace(self, ssh):
        run_basepath = self.basepath+"/"+self.run_id
        ssh.exec_command(f"rm -rf {run_basepath}")
        sftp = ssh.open_sftp()

        if not sftp_exists(sftp, run_basepath):
            print(f"Creating run_basepath: {run_basepath}")
            sftp.mkdir(run_basepath)
            sftp.mkdir(run_basepath+"/app")
        sftp.close()
        return run_basepath

    def _transfer_files(self, files, run_path, ssh):
        sftp = ssh.open_sftp()
        for file in files:
            sftp.put(file, run_path + "/app/" + os.path.basename(file))
        sftp.close()

    def _upload_project(self, project_dir, run_path, ssh):
        project_archive = "_source.tar.gz"
        self._make_tarfile(project_archive, project_dir)
        self._transfer_files([os.path.join(project_dir, project_archive)], run_path, ssh)

    def init(self, run_id, datarefs):
        self.run_id = run_id
        self.client = docker.DockerClient(base_url=f'tcp://{self.server}:2375', timeout=10)
        ssh = paramiko.SSHClient()
        ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        ssh.connect(self.server, username=self.username, password=self.password)

        print("Initializing data references")
        for ref in datarefs:
            ref.build(self.basepath, run_id)

        print("Initializing workspace")
        run_path = self._init_workspace(ssh)

        print("Uploading project files")
        self._upload_project(os.getcwd(), run_path, ssh)
        ssh.close()

        print("Building docker context...")
        tarbuf = BytesIO()
        with tarfile.open(fileobj=tarbuf, mode="w") as tar:
            tar.add("flow/dockerimages/Dockerfile", "Dockerfile")
            tar.add("flow/dockerimages/entrypoint.sh", "entrypoint.sh")
            tar.add("flow/dockerimages/entrypoint.py", "entrypoint.py")
            tar.close()

        print("Building docker image")
        self.client.images.build(fileobj=tarbuf.getvalue(),
                            custom_context=True,
                            dockerfile="Dockerfile",
                            tag="pythonimage",
                            encoding="utf-8")

    def execute(self, run_id, script_name, script_arguments, datarefs):
        print("ALL CONTAINERS:")
        containers_list = self.client.containers.list(all=True)
        print(containers_list)
        volums = dict()
        app_path = f"{self.basepath}/{run_id}/app"
        volums[app_path] = {
            "bind": "/app",
            "mode": "rw"
        }
        log_path = f"{self.basepath}/{run_id}/logs"
        volums[log_path] = {
            "bind": "/logs",
            "mode": "rw"
        }
        for ref in datarefs:
            vol = {
                    "bind": ref.container_path,
                    "mode": "rw"
                }
            volums[ref.host_path] = vol

        print("Staring container...")
        _args = " ".join([str(a) for a in script_arguments])
        self.container = self.client.containers.run(
            image="pythonimage",
            name=f"python_container_{np.random.randint(1000)}",
            hostname=f'tcp://{self.server}:2375',
            command=f"./entrypoint.sh app {script_name} {_args}",
            volumes = volums,
            stdout=True,
            stderr=True,
            detach=True)

        def read_log(_container):
            logs = _container.logs(stream=True)
            for line in logs:
                log_line = line.decode("UTF-8").strip()
                self.run_log.append(log_line)
                print(f"LOG: {log_line}")

        thread = threading.Thread(read_log(self.container))
        thread.start()
        self.exit_code = self.container.wait()["StatusCode"]
        self.container.remove()

        return self.exit_code


class BaseStep:
    def __init__(self):
        pass


class PythonScriptStep(BaseStep):
    def __init__(self, script_name, arguments, datarefs, compute_target):
        super().__init__()
        self.compute_target = compute_target
        self.datarefs = datarefs
        self.arguments = arguments
        self.script_name = script_name

    def run(self, run_id):
        exit_code = self.compute_target.execute(run_id=run_id, script_name=self.script_name, script_arguments=self.arguments, datarefs=self.datarefs)

        return exit_code


class Flow:
    def __init__(self):
        self.steps = []
        self.datarefs = []

    def add(self, step):
        self.steps.append(step)
        return self

    def add_datarefs(self, datarefs):
        self.datarefs += datarefs
        return self

    def add_data_reference(self, path):
        ref = DataReference(path)
        self.datarefs.append(ref)
        return ref

    def run(self, run_id):
        for step in self.steps:
            step.compute_target.init(run_id, self.datarefs)
            exit_code = step.run(run_id)
            if exit_code != 0:
                print("Error")
                break

        return self

