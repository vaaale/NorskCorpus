import os
import tarfile

import requests

from flow.utils import gather_files
import json
import uuid


class DataReference:

    def __init__(self, path):
        self.path = path
        self.name = uuid.uuid4().__str__()

    def build(self):
        return {"name": self.name, "path": self.path}

    def __str__(self):
        return self.name


class ComputeTarget:
    def __init__(self, name, type="python"):
        self.name = name
        self.type = type

    def build(self):
        compute_json = {
            "name": self.name,
            "type": self.type
        }
        return compute_json


class BaseStep:
    def __init__(self, type):
        self.type = type


class PythonScriptStep(BaseStep):
    def __init__(self, script_name, arguments, source_directory, datarefs, compute_target):
        super().__init__("PythonStep")
        self.compute_target = compute_target
        self.datarefs = datarefs
        self.source_directory = source_directory
        self.arguments = arguments
        self.script_name = script_name

    def build(self):
        datarefs_json = []
        for ref in self.datarefs:
            datarefs_json.append(ref.name)
        args_json = []
        for arg in self.arguments:
            if isinstance(arg, DataReference):
                args_json.append(str(arg))
            else:
                args_json.append(arg)

        step_json = {
            "step_type": self.type,
            "script_name": self.script_name,
            "source_directory": self.source_directory,
            "arguments": args_json,
            "compute_target": self.compute_target.name,
            "datarefs": datarefs_json
        }
        return step_json


class Flow:

    COMPUTE_TYPE_PYTHON = "python"
    COMPUTE_TYPE_NVIDIA = "nvidia"

    def __init__(self, server="localhost", username=None, password=None, source_root="."):
        self.source_root = source_root
        self.password = password
        self.username = username
        self.server = server
        self.steps = []
        self.datarefs = []
        self.computes = []

    def _make_tarfile(self):
        archive_name = "_source.tar.gz"
        files = gather_files(self.source_root)
        archive_path = os.path.join(self.source_root, archive_name)
        with tarfile.open(archive_path, "w:gz") as tar:
            for file in files:
                _file = os.path.relpath(file, self.source_root).replace('\\', '/')
                tar.add(file, _file)
            tar.close()
        return archive_path

    def _compute_exists(self, compute):
        for c in self.computes:
            if c.name == compute.name:
                return True
        return False

    def _dataref_exist(self, path):
        for r in self.datarefs:
            if r.path == path:
                return True
        return False

    def add(self, step):
        if not self._compute_exists(step.compute_target):
            self.computes.append(step.compute_target)
        self.steps.append(step)
        return self

    def add_data_reference(self, path):
        ref = DataReference(path)
        if not self._dataref_exist(path):
            self.datarefs.append(ref)

        return ref

    def _build(self):
        runconfig = {"steps": []}
        for step in self.steps:
            step_json = step.build()
            runconfig["steps"].append(step_json)

        runconfig["computes"] = []
        for compute in self.computes:
            runconfig["computes"].append(compute.build())

        runconfig["datarefs"] = []
        for ref in self.datarefs:
            runconfig["datarefs"].append(ref.build())

        return runconfig

    def run(self, run_id=None):
        run_config = self._build()
        run_config['run_id'] = run_id
        archive_path = self._make_tarfile()

        run_json = json.dumps(run_config)
        with open(archive_path, "rb") as fin:
            files = {'file': fin}
            r = requests.post(f"http://{self.server}:5000", files=files, data={'run_config': run_json})
            print(r.text)
