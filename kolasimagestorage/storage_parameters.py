from typing import Dict


class StorageParameters:
    def __init__(self, driver_name: str, storage_driver_parameters: Dict[str, str], container_name: str):
        self.driver_name = driver_name
        self.driver_parameters = storage_driver_parameters
        self.container_name = container_name

