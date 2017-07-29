import datetime
import logging
import uuid

import numpy as np

from kolasimagestorage.storage_parameters import StorageParameters
from kolasimagestorage.file_service import FileService
from kolasimagestorage import ImageEncoder


class ImageServiceError(Exception): pass


class ImageSavingFailed(ImageServiceError): pass


class ImageReadingFailed(ImageServiceError): pass


class ImageService:
    FORMAT = "jpeg"

    def __init__(self, storage_params: StorageParameters):
        logger = logging.getLogger(__name__)
        logger.info("Init ImageService for url {}".format(storage_params))

        self._file_storage = FileService(storage_params)

        self._image_encoder = ImageEncoder(self.FORMAT)

    def _create_name(self):
        return "{}_{}.{}".format(datetime.datetime.utcnow().isoformat(), str(uuid.uuid4()), self.FORMAT)

    def put_array(self, image: np.ndarray) -> str:
        binary = self._image_encoder.numpy_to_binary(image)
        return self.put_encoded(binary)

    def get_array(self, path: str) -> np.ndarray:
        try:
            binary = self._file_storage.get(location=path)
        except Exception as e:
            raise ImageReadingFailed("Reading image from '{}' failed".format(path)) from e
        return self._image_encoder.binary_to_array(binary)

    def put_encoded(self, image: bytes) -> str:
        try:
            return self._file_storage.put(image, self._create_name())
        except Exception as e:
            raise ImageSavingFailed() from e

    def get_encoded(self, path: str) -> bytes:
        try:
            return self._file_storage.get(location=path)
        except Exception as e:
            raise ImageReadingFailed("Reading image from '{}' failed".format(path)) from e
