import pytest

from kolasimagestorage import StorageParameters


class TestStorageParameters:
    def test_storage_parameters(self):
        parameters = StorageParameters("driver_name", {"key": "our_key", "pass": "pass"}, "container")
        assert parameters.driver_name == "driver_name"
        assert parameters.driver_parameters["key"] == "our_key"
        assert parameters.container_name == "container"

    def test_fails_without_key(self):
        with pytest.raises(Exception):
            StorageParameters("driver_name", {"pass": "pass"}, "container")
