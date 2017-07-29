import datetime
import uuid

import libcloud.storage.providers
from libcloud.storage.types import ContainerAlreadyExistsError
from six import BytesIO

from kolasimagestorage import StorageParameters


class FileServiceException(Exception):
    pass




class FileService:
    def __init__(self, storage_parameters: StorageParameters):
        driver_cls = libcloud.storage.providers.get_driver(storage_parameters.driver_name)
        driver = driver_cls(**storage_parameters.driver_parameters)

        self.container = self._get_container(driver, storage_parameters.container_name)

    @staticmethod
    def _get_container(driver, container_name: str):
        try:
            driver.create_container(container_name=container_name)
        except ContainerAlreadyExistsError:
            pass
        return driver.get_container(container_name=container_name)

    def put(self, file_content: bytes, file_name: str) -> str:
        if not isinstance(file_content, bytes):
            raise FileServiceException("Type of data is incorrect. Only bytes format is supported")
        data = BytesIO(file_content)
        try:
            self.container.upload_object_via_stream(iterator=data, object_name=file_name)
        except Exception as e:
            raise FileServiceException("failed to save image") from e
        return file_name

    def get(self, location: str) -> bytes:
        try:
            obj = self.container.get_object(location)
            return b''.join(obj.as_stream())
        except Exception as e:
            raise FileServiceException("Unable read file with id '{}'") from e
