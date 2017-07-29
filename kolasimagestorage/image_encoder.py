import numpy as np
from PIL import Image
from io import BytesIO


class ImageEncoder:
    def __init__(self, image_format: str):
        self._format = image_format

    def numpy_to_binary(self, image: np.ndarray) -> bytes:
        im = Image.fromarray(np.uint8(image))
        file_like = BytesIO()
        im.save(file_like, format=self._format)
        return file_like.getvalue()

    # noinspection PyMethodMayBeStatic
    def binary_to_array(self, binary: bytes) -> np.ndarray:
        return np.asarray(Image.open(BytesIO(binary)))
