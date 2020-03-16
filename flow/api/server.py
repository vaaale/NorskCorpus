from flask import Flask, request, redirect, url_for, send_from_directory
import json
import os

from flow.flow import PythonScriptStep, DataReference, ComputeTarget, Flow

app = Flask(__name__)
UPLOAD_FOLDER="/tmp"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


server = "localhost"
username = "compute"
password = "compute"


def allowed_file(filename):
    return ".tar" in filename

def build_datarefs(configs):
    refs = {}
    for config in configs:
        ref = DataReference(config["path"])
        refs[config["name"]] = ref
    return refs

def build_computes(configs):
    compute_list = {}
    for config in configs:
        compute_type = config["type"]
        if "python" == compute_type:
            target = ComputeTarget(server=server, username=username, password=password)
            compute_list[config["name"]] = target
        elif "cuda" == compute_type:
            raise Exception("Compute type Cuda is not implemented yet")
    return compute_list

def parse_arguments(arguments):
    res = {"datarefs": []}
    for a in arguments:
        if isinstance(a, dict):
            if a["type"] == "DATAREF":
                res["datarefs"].append(a)

    return res

def get_datarefs(datarefs, step_datarefs):
    res = []
    for name in step_datarefs:
        res.append(datarefs[name])
    return res

def build_job(run_config, source):
    steps = run_config['steps']
    computes = build_computes(run_config["computes"])
    datarefs = build_datarefs(run_config["datarefs"])
    flow = Flow()
    for step in steps:
        if step["step_type"] == "PythonStep":
            step_datarefs = get_datarefs(datarefs, step["datarefs"])

            step = PythonScriptStep(script_name=step["script_name"],
                                    arguments=step["arguments"],
                                    datarefs=step_datarefs,
                                    compute_target=computes[step["compute_target"]])

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