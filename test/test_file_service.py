import uuid

import pytest
import requests
from pytest import mark

from kolasimagestorage.file_service import FileService, FileNotFoundException, WrongFileId, IncorrectFile
from test.seaweedfs_utils import SeaWeedFSConnection
from test.seaweedfs_utils import seaweedfs_slave


@pytest.fixture(scope="module")
def seaweedfs(request):
    with seaweedfs_slave(19331, 18082) as seaweed_url:
        yield SeaWeedFSConnection(seaweed_url)


class TestFileStorage:
    data1 = b"data1"
    data2 = b"data2"

    def test_put_and_get(self, seaweedfs):
        file_service = FileService(seaweedfs.url)

        file1_id = file_service.put(self.data1)
        file2_id = file_service.put(self.data2)

        loaded_data1 = file_service.get(file1_id)
        loaded_data2 = file_service.get(file2_id)
        loaded_data3 = file_service.get(file1_id)

        assert self.data1 == loaded_data1
        assert self.data2 == loaded_data2
        assert self.data1 == loaded_data3

    def test_non_existent(self, seaweedfs):
        file_service = FileService(seaweedfs.url)

        with pytest.raises(FileNotFoundException):
            file_service.get("non-existent-id-" + str(uuid.uuid4()))

    # noinspection PyTypeChecker
    def test_wrong_id_type(self, seaweedfs):
        image_service = FileService(seaweedfs.url)

        with pytest.raises(WrongFileId):
            image_service.get(b"123123")

        with pytest.raises(WrongFileId):
            image_service.get([[1, 2, 3, 4]])

    # noinspection PyTypeChecker
    def test_wrong_image_type(self, seaweedfs):
        image_service = FileService(seaweedfs.url)

        with pytest.raises(IncorrectFile):
            image_service.put("123123")

        with pytest.raises(IncorrectFile):
            image_service.put([[1, 2, 3, 4]])


@mark.skip(reason="dummy test")
class TestSeaweedFS:
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
