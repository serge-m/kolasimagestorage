from unittest import mock
from unittest.mock import call

import numpy as np
import pytest

from six import BytesIO

from kolasimagestorage.image_service import ImageService
# noinspection PyUnresolvedReferences
from fixtures import storage_params


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


class MatchingString:
    def __init__(self):
        self.history = []

    def __eq__(self, other):
        if type(other) != str:
            return False
        self.history.append(other)
        return True


class TestImageService:
    image = np.arange(0, 256).reshape(8, 32)

    bytes_array = b"some-bytes"
    url = "urllll"

    @mock.patch('kolasimagestorage.image_service.ImageEncoder')
    @mock.patch('kolasimagestorage.image_service.FileService')
    def test_creation(self, mocked_file_service, mocked_image_endoder, storage_params):
        ImageService(storage_params)

        mocked_image_endoder.assert_called_once_with("jpeg")
        mocked_file_service.assert_called_once_with(storage_params)

    @mock.patch('kolasimagestorage.image_service.ImageEncoder')
    @mock.patch('kolasimagestorage.image_service.FileService')
    def test_put(self, mocked_file_service, mocked_image_endoder, storage_params):
        mocked_image_endoder.return_value.numpy_to_binary.return_value = self.bytes_array
        mocked_file_service.return_value.put.return_value = self.url

        path = ImageService(storage_params).put_array(self.image)

        assert path == self.url
        mocked_image_endoder.return_value.numpy_to_binary.assert_called_once_with(self.image)
        mocked_file_service.return_value.put.assert_called_once_with(self.bytes_array, MatchingString())

    @mock.patch('kolasimagestorage.image_service.ImageEncoder')
    @mock.patch('kolasimagestorage.image_service.FileService')
    def test_put_generates_random_unique_paths(self, mocked_file_service, mocked_image_endoder, storage_params):
        mocked_image_endoder.return_value.numpy_to_binary.return_value = self.bytes_array

        service = ImageService(storage_params)
        service.put_array(self.image)
        service.put_array(self.image)

        matcher = MatchingString()
        mocked_file_service.return_value.put.assert_has_calls([call(self.bytes_array, matcher),
                                                               call(self.bytes_array, matcher),
                                                               ])
        assert matcher.history[0] != matcher.history[1]

    @mock.patch('kolasimagestorage.image_service.ImageEncoder')
    @mock.patch('kolasimagestorage.image_service.FileService')
    def test_get(self, mocked_file_service, mocked_image_endoder, storage_params):
        mocked_file_service.return_value.get.return_value = self.bytes_array
        mocked_image_endoder.return_value.binary_to_array.return_value = self.image

        image = ImageService(storage_params).get_array(self.url)

        assert image is self.image
        mocked_file_service.return_value.get.assert_called_once_with(location=self.url)
        mocked_image_endoder.return_value.binary_to_array.assert_called_once_with(self.bytes_array)

    # noinspection PyTypeChecker
    def test_wrong_image_type(self, storage_params):
        image_service = ImageService(storage_params)

        with pytest.raises(Exception):
            image_service.put_array("123123")

        with pytest.raises(Exception):
            image_service.put_array([[1, 2, 3, [4]]])
