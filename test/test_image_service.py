from unittest import mock

import numpy as np
import pytest
from six import BytesIO

from image_service import ImageService


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


class TestImageService:
    image = np.arange(0, 256).reshape(8, 32)

    url = "some-url"
    bytes_array = b"some-bytes"

    @mock.patch('image_service.ImageEncoder')
    @mock.patch('image_service.FileService')
    def test_creation(self, mocked_file_service, mocked_image_endoder):
        ImageService(self.url)

        mocked_image_endoder.assert_called_once_with("jpeg")
        mocked_file_service.assert_called_once_with(self.url)

    @mock.patch('image_service.ImageEncoder')
    @mock.patch('image_service.FileService')
    def test_put(self, mocked_file_service, mocked_image_endoder):
        mocked_image_endoder.return_value.numpy_to_binary.return_value = self.bytes_array
        mocked_file_service.return_value.put.return_value = self.url

        path = ImageService(self.url).put_array(self.image)

        assert path == self.url
        mocked_image_endoder.return_value.numpy_to_binary.assert_called_once_with(self.image)
        mocked_file_service.return_value.put.assert_called_once_with(self.bytes_array)

    @mock.patch('image_service.ImageEncoder')
    @mock.patch('image_service.FileService')
    def test_get(self, mocked_file_service, mocked_image_endoder):
        mocked_file_service.return_value.get.return_value = self.bytes_array
        mocked_image_endoder.return_value.binary_to_array.return_value = self.image

        image = ImageService(self.url).get_array(self.url)

        assert image is self.image
        mocked_file_service.return_value.get.assert_called_once_with(file_id=self.url)
        mocked_image_endoder.return_value.binary_to_array.assert_called_once_with(self.bytes_array)

    def test_wrong_image_type(self):
        image_service = ImageService(self.url)

        with pytest.raises(Exception):
            image_service.put_array("123123")

        with pytest.raises(Exception):
            image_service.put_array([[1, 2, 3, [4]]])
