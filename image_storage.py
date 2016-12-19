import requests
import numpy as np


class ImageStorage:
    def __init__(self, url):
        self.url = url

    def save(self, image: np.ndarray)-> str:
        pass

    def load(self, path: str) -> np.ndarray:
        pass