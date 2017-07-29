import shutil

import pytest
import tempfile

from kolasimagestorage import StorageParameters


@pytest.fixture
def storage_params():
    tmp_storage_location = tempfile.mkdtemp()
    yield StorageParameters(driver_name="local", storage_driver_parameters=dict(key=tmp_storage_location),
                            container_name="test_container", )
    shutil.rmtree(tmp_storage_location)
