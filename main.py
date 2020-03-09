import os
from flow.flow import Flow, PythonScriptStep, ComputeTarget

server = "192.168.163.130"
username = "compute"
password = "compute"

flow = Flow()
compute_target = ComputeTarget(server, username, password)

input_data = flow.add_data_reference(path="archives")
output_data = flow.add_data_reference(path="rawtext")

process_arguments = ["--input", input_data, "--output", output_data]
flow = flow.add(PythonScriptStep(
    script_name="build_corpus.py",
    datarefs=[input_data, output_data],
    arguments=process_arguments,
    source_directory=os.getcwd(),
    compute_target=compute_target
))


flow.run("run_2")

