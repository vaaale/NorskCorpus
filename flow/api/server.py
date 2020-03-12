from flask import Flask, request, redirect, url_for, send_from_directory
import json
import os

from flow.flow import PythonScriptStep, DataReference, ComputeTarget

app = Flask(__name__)
UPLOAD_FOLDER="/tmp"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


server = "localhost"
username = "compute"
password = "compute"


def allowed_file(filename):
    return ".tar" in filename

def build_datarefs(configs):
    refs = []
    for config in configs:
        ref = DataReference(config["path"])
        refs.append(ref)
    return refs

def build_computes(configs):
    compute_list = []
    for config in configs:
        compute_type = config["type"]
        if "python" == compute_type:
            target = ComputeTarget(server=server, username=username, password=password)
            compute_list.append(target)
        elif "cuda" == compute_type:
            raise Exception("Compute type Cuda is not implemented yet")
    return compute_list

def build_arguments(config, datarefs):
    arguments = []
    for a in config:
        if isinstance(a, str):
            arguments.append(a)
        elif isinstance(a, dict):
            if a["type"] == "DATAREF":
                pass


def build_job(config, source):
    configs = config['steps']
    computes = build_computes(config["computes"])
    datarefs = build_datarefs(config["datarefs"])
    for config in configs:
        if config["step_type"] == "PythonStep":

            arguments = build_arguments(config["arguments"], datarefs)

            step = PythonScriptStep(script_name=config["script_name"])

    print("")

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        json_data = request.form.get("run_config")
        data = json.loads(json_data)
        tar_archive_name = file.filename
        if file and allowed_file(tar_archive_name):
            print('**found file', tar_archive_name)
            tar_path = os.path.join(app.config['UPLOAD_FOLDER'], tar_archive_name)
            file.save(tar_path)
            build_job(data, tar_path)


    return f'{"run": {data.run_id}, "status": "Started"}'

if __name__ == '__main__':
    app.run()