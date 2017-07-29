import pytest

from kolasimagestorage.file_service import FileService,  FileServiceException
# noinspection PyUnresolvedReferences
from fixtures import storage_params


# noinspection PyShadowingNames
class TestFileStorage:
    data1 = b"data1"
    data2 = b"data2"

    def test_put_and_get(self, storage_params):
        file_service = FileService(storage_params)

        file1_id = file_service.put(self.data1, "path1")
        file2_id = file_service.put(self.data2, "path2")

        loaded_data1 = file_service.get(file1_id)
        loaded_data2 = file_service.get(file2_id)
        loaded_data3 = file_service.get(file1_id)

        assert self.data1 == loaded_data1
        assert self.data2 == loaded_data2
        assert self.data1 == loaded_data3

    def test_non_existent(self, storage_params):
        file_service = FileService(storage_params)

        with pytest.raises(FileServiceException):
            file_service.get("non-existent-id")

    # noinspection PyTypeChecker
    def test_wrong_id_type(self, storage_params):
        image_service = FileService(storage_params)

        with pytest.raises(FileServiceException):
            image_service.get(b"123123")

        with pytest.raises(FileServiceException):
            image_service.get([[1, 2, 3, 4]])

    # noinspection PyTypeChecker
    def test_wrong_image_type(self, storage_params):
        image_service = FileService(storage_params)

        with pytest.raises(FileServiceException):
            image_service.put("123123", "some_path")

        with pytest.raises(FileServiceException):
            image_service.put([[1, 2, 3, 4]], "some_path")
