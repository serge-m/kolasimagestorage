from typing import Dict


class StorageParameters:
    def __init__(self, driver_name: str, storage_driver_parameters: Dict[str, str], container_name: str):
        if "key" not in storage_driver_parameters:
            raise RuntimeError("key must be specified for storage driver")
        self.driver_name = driver_name
        self.driver_parameters = storage_driver_parameters
        self.container_name = container_name

    def __eq__(self, other):
        if isinstance(other, StorageParameters):
            return self.__dict__ == other.__dict__
        raise NotImplementedError("Comparison not implemented for a given type")
