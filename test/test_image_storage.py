import subprocess
import shlex
import requests
import contextlib

import pytest

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
                        '{docker_image} volume -max=5 -mserver="localhost:9333" -port=8080'.format(
                docker_image=docker_image,
                master_id=master
            )))
        container_id = container_id.decode('utf8').strip()
        yield "http://localhost:9333/"
        subprocess.check_output(['docker', 'rm', '-f', container_id])


class SeaWeedFSConnection:
    def __init__(self, url):
        self.url = url


@pytest.fixture(scope="module")
def seaweedfs(request):
    with seaweedfs_slave() as seaweed_url:
        yield SeaWeedFSConnection(seaweed_url)


class TestImageStorage:
    def test1(self, seaweedfs):
        url = seaweedfs.url
        response = requests.get(url)
        assert response.status_code == 200


        # def teardown_method(self, test_method):
        #     subprocess.check_call(['docker', 'rm', '-f', self.container])
        #
        # def test_listening_port80(self):
        #     out = subprocess.check_output("netstat -lnt | awk '$6 == \"LISTEN\" && $4 ~ \"80$\"'",
        #                                   shell=True)
        #     assert out != ""
        #
        # def test_working_http(self):
        #     subprocess.check_call(['curl', 'localhost'])
        #
        # def test_saving(self):
        #     ImageStorage("http://localhost:")
