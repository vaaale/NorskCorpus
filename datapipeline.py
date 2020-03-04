import azureml.core

from azureml.core.authentication import InteractiveLoginAuthentication
from azureml.core import Workspace, Environment, Datastore, Experiment
from azureml.core.model import InferenceConfig, Model
from azureml.core.webservice import AciWebservice, Webservice
from azureml.core.compute import ComputeTarget, AmlCompute
from azureml.core.runconfig import RunConfiguration

from azureml.exceptions import WebserviceException
from azureml.data.data_reference import DataReference

from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import PipelineData, Pipeline
import json
import os


with open('config.json', 'r') as jsonfile:
    ws_config = json.load(jsonfile)

interactive_auth = InteractiveLoginAuthentication(tenant_id=ws_config['tenantId'])

ws = Workspace(
    subscription_id=ws_config['subscription_id'],
    resource_group=ws_config['resource_group'],
    workspace_name=ws_config['workspace_name'],
    auth=interactive_auth,
)

datastore_name='shiftdatastore' # Name of the datastore to workspace
container_name=os.getenv("BLOB_CONTAINER", "news20container") # Name of Azure blob container
account_name=os.getenv("BLOB_ACCOUNTNAME", "shiftreference") # Storage account name
account_key=os.getenv("AZURE_STORAGE_KEY") # Storage account key

datastore = Datastore.get(ws, "shiftdatastore")


blob_datastore = Datastore.register_azure_blob_container(workspace=ws,
                                                         datastore_name=datastore_name,
                                                         container_name=container_name,
                                                         account_name=account_name,
                                                         account_key=account_key)
