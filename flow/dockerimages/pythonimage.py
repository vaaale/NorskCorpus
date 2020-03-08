import tarfile
from io import BytesIO
import docker

from flow.flow import upload_project

client = docker.DockerClient(base_url='tcp://192.168.163.130:2375', timeout=10)

print("Building docker context...")
tarbuf = BytesIO()
with tarfile.open(fileobj=tarbuf, mode="w") as tar:
    tar.add("Dockerfile")
    # tar.add("main.py")
    tar.add("entrypoint.sh")
    tar.close()

print("Building docker image")
client.images.build(fileobj=tarbuf.getvalue(),
                    custom_context=True,
                    dockerfile="Dockerfile",
                    tag="pythonimage",
                    encoding="utf-8")

print("Uploading project files")
upload_project("../../")

print("Staring container...")
container = client.containers.run(image="pythonimage",
                                  name="python_container",
                                  hostname='tcp://192.168.163.130:2375',
                                  command="./entrypoint.sh main.py",
                                  volumes={
                                      '/home/compute/app': {
                                          'bind': '/app',
                                          'mode': 'rw'
                                      }
                                  },
                                  remove=True,
                                  stdout=True,
                                  stderr=True,
                                  detach=True)

logs = container.logs(stream=True)

for line in logs:
    print(line.decode("UTF-8").strip())

client.close()