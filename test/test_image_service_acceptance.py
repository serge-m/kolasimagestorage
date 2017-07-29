import shutil

import numpy as np
import pytest
import tempfile

from kolasimagestorage.image_service import ImageService
# noinspection PyUnresolvedReferences
from fixtures import storage_params


class TestImageServiceAcceptance:
    image = np.arange(0, 256).reshape(8, 32)

    url = "some-url"
    bytes_array = b"some-bytes"

    def test_put_get(self, storage_params):
        image_service = ImageService(storage_params)
        path = image_service.put_array(self.image)
        loaded = image_service.get_array(path)

        assert isinstance(path, str)
        assert np.allclose(loaded, self.image, atol=2)
