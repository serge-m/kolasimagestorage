import logging
import numpy as np

from kolasimagestorage.file_service import FileService
from kolasimagestorage.image_encoder import ImageEncoder


class ImageServiceError(Exception): pass


class ImageSavingFailed(ImageServiceError): pass


class ImageReadingFailed(ImageServiceError): pass


class ImageService:
    def __init__(self, url):
        logger = logging.getLogger(__name__)
        logger.info("Init ImageService for url {}".format(url))

        self._file_storage = FileService(url)
        self._image_encoder = ImageEncoder("jpeg")

    def put_array(self, image: np.ndarray) -> str:
        binary = self._image_encoder.numpy_to_binary(image)
        try:
            return self._file_storage.put(binary)
        except Exception as e:
            raise ImageSavingFailed() from e

    def get_array(self, path: str) -> np.ndarray:
        try:
            binary = self._file_storage.get(file_id=path)
        except Exception as e:
            raise ImageReadingFailed("Reading image from '{}' failed".format(path)) from e
        return self._image_encoder.binary_to_array(binary)

    def put_encoded(self, image: bytes) -> str:
        try:
            return self._file_storage.put(image)
        except Exception as e:
            raise ImageSavingFailed() from e

    def get_encoded(self, path: str) -> bytes:
        try:
            return self._file_storage.get(file_id=path)
        except Exception as e:
            raise ImageReadingFailed("Reading image from '{}' failed".format(path)) from e
