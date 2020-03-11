import os
from flow.flowapi import Flow, PythonScriptStep, ComputeTarget

# server = "192.168.163.130"
server = "localhost"
username = "compute"
password = "compute"

flow = Flow(server=server)
compute_target = ComputeTarget(name="my_compute", type=Flow.COMPUTE_TYPE_PYTHON)

input_data = flow.add_data_reference(path="archives")
output_data = flow.add_data_reference(path="rawtext")

flow = flow.add(PythonScriptStep(
    script_name="build_corpus.py",
    arguments=["--input", input_data, "--output", output_data],
    datarefs=[input_data, output_data],
    source_directory=os.getcwd(),
    compute_target=compute_target
)).add(PythonScriptStep(
    script_name="cat_output.py",
    arguments=["--input", output_data],
    datarefs=[output_data],
    source_directory=os.getcwd(),
    compute_target=compute_target
))


flow.run("run_2")

