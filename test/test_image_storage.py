import subprocess
import shlex

import numpy as np
import requests
import contextlib

import pytest
from six import BytesIO

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


@pytest.fixture(scope="module")
def seaweedfs(request):
    with seaweedfs_slave() as seaweed_url:
        yield SeaWeedFSConnection(seaweed_url)


class ImageServiceException(Exception):
    pass


class ImageNotFoundException(ImageServiceException):
    pass


class IncorrectImage(ImageServiceException):
    pass


class ImageService:
    def __init__(self, url):
        self._storage_url = url

    def put(self, image: bytes) -> str:
        return ""

    def get(self, image_id: str) -> bytes:
        return b""


def load_image(path):
    with open(path, "rb") as file:
        return file.read()


def prepare_test_image():
    from PIL import Image
    arr = np.ones([100, 100], dtype='uint8') * 128
    im = Image.fromarray(arr)
    file_like = BytesIO()
    im.save(file_like, format='jpeg')
    return file_like.getvalue()


class TestImageStorage:
    image1 = load_image("./test_data/test.jpg")
    image2 = prepare_test_image()

    def test_alive(self, seaweedfs):
        url = seaweedfs.url
        response = requests.get(url)
        assert response.status_code == 200

    def test_file_upload(self, seaweedfs):
        url = seaweedfs.url + "dir/assign"
        response_creation = requests.post(url)
        json = response_creation.json()
        fid = json['fid']
        url = json['publicUrl']
        with open("./test_data/test.jpg", "rb") as file:
            response = requests.put("http://" + url + "/" + fid, files={'file': file})
        print(response)

        lookup = requests.get(seaweedfs.url + "/dir/lookup?volumeId=" + fid)
        print(lookup)
        read_url = lookup.json()["locations"][0]["publicUrl"]
        response1 = requests.get("http://" + read_url + "/" + fid)
        print(response1.content)

    def test_put_and_get(self, seaweedfs):
        image_service = ImageService(seaweedfs.url)

        image1_id = image_service.put(self.image1)
        image2_id = image_service.put(self.image2)

        loaded_image1 = image_service.get(image1_id)
        loaded_image2 = image_service.get(image2_id)

        assert self.image1 == loaded_image1
        assert self.image2 == loaded_image2

    def test_non_existent(self, seaweedfs):
        image_service = ImageService(seaweedfs.url)

        with pytest.raises(ImageNotFoundException):
            image_service.get("non-existent-id")

    def test_wrong_image_type(self, seaweedfs):
        image_service = ImageService(seaweedfs.url)

        with pytest.raises(IncorrectImage):
            image_service.put("123123")

        with pytest.raises(IncorrectImage):
            image_service.put([[1, 2, 3, 4]])

    def test_wrong_id_type(self, seaweedfs):
        image_service = ImageService(seaweedfs.url)

        with pytest.raises(IncorrectImage):
            image_service.get(b"123123")

        with pytest.raises(IncorrectImage):
            image_service.get([[1, 2, 3, 4]])



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
