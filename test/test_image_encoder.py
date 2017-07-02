import numpy as np

from kolasimagestorage.image_encoder import ImageEncoder


class TestImageEncoder:
    range256 = np.arange(256, dtype='uint8')
    row = np.vstack([range256]*64 + [range256//2]*32)

    def test_conversion(self):
        encoder = ImageEncoder("jpeg")
        encoded = encoder.numpy_to_binary(self.row)
        decoded = encoder.binary_to_array(encoded)

        assert isinstance(encoded, bytes)
        assert len(encoded) > 0
        assert np.allclose(self.row, decoded, atol=1)
