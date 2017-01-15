import contextlib
import shlex
import subprocess

docker_image = "chrislusf/seaweedfs"
master_original_port = 9333


@contextlib.contextmanager
def seaweedfs_master(master_port):
    container_id = subprocess.check_output(
        shlex.split("docker run -d -p {master_port}:{master_original_port} {docker_image} master".format(
            docker_image=docker_image,
            master_port=master_port,
            master_original_port=master_original_port)))
    container_id = container_id.decode('utf8').strip()
    yield container_id
    subprocess.check_output(['docker', 'rm', '-f', container_id])


@contextlib.contextmanager
def seaweedfs_slave(master_port, slave_port):
    with seaweedfs_master(master_port=master_port) as master:
        command_base = 'docker run -d -p {slave_port}:{slave_port} --link {master_id} {docker_image} ' .format(
            docker_image=docker_image, master_id=master, slave_port=slave_port)
        command_tail = ' volume -max=5 -mserver="{master_id}:{master_original_port}" -port={slave_port}' .format(
            master_id=master, slave_port=slave_port, master_original_port=master_original_port)
        command = command_base + command_tail
        container_id = subprocess.check_output(shlex.split(command))
        container_id = container_id.decode('utf8').strip()
        yield "http://localhost:{master_port}/".format(master_port=master_port)
        subprocess.check_output(['docker', 'rm', '-f', container_id])


class SeaWeedFSConnection:
    def __init__(self, url):
        self.url = url
