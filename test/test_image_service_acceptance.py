import numpy as np
import pytest

from image_service import ImageService
from test.seaweedfs_utils import SeaWeedFSConnection
from test.seaweedfs_utils import seaweedfs_slave


@pytest.fixture(scope="module")
def seaweedfs(request):
    with seaweedfs_slave(19334, 18081) as seaweed_url:
        yield SeaWeedFSConnection(seaweed_url)


class TestImageServiceAcceptance:
    image = np.arange(0, 256).reshape(8, 32)

    url = "some-url"
    bytes_array = b"some-bytes"

    def test_put_get(self, seaweedfs):
        image_service = ImageService(seaweedfs.url)
        path = image_service.put(self.image)
        loaded = image_service.get(path)

        assert isinstance(path, str)
        assert np.allclose(loaded, self.image, atol=2)
