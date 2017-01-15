import contextlib
import shlex
import subprocess

docker_image = "chrislusf/seaweedfs"


@contextlib.contextmanager
def seaweedfs_master():
    container_id = subprocess.check_output(
        shlex.split("docker run -d -p 9333:9333 {docker_image} master".format(docker_image=docker_image)))
    container_id = container_id.decode('utf8').strip()
    yield container_id
    subprocess.check_output(['docker', 'rm', '-f', container_id])


@contextlib.contextmanager
def seaweedfs_slave():
    with seaweedfs_master() as master:
        container_id = subprocess.check_output(
            shlex.split('docker run -d -p 8080:8080 --link {master_id} '
                        '{docker_image} volume -max=5 -mserver="{master_id}:9333" -port=8080'.format(
                docker_image=docker_image,
                master_id=master
            )))
        container_id = container_id.decode('utf8').strip()
        yield "http://localhost:9333/"
        subprocess.check_output(['docker', 'rm', '-f', container_id])


class SeaWeedFSConnection:
    def __init__(self, url):
        self.url = url
