import requests
from six import BytesIO


class FileServiceException(Exception):
    pass


class WrongFileId(FileServiceException):
    pass


class FileNotFoundException(FileServiceException):
    pass


class IncorrectFile(FileServiceException):
    pass


class FileService:
    protocol = "http://"
    url_delimiter = "/"

    def __init__(self, url):
        self._storage_url = url

    def put(self, file_content: bytes) -> str:
        if not isinstance(file_content, bytes):
            raise IncorrectFile("Type of data is incorrect. Only bytes format is supported")
        fid, write_location = self._create_location()
        self._write_data(file_content, write_location)
        return fid

    def get(self, file_id: str) -> bytes:
        read_url = self._find_file_location(file_id)
        return self._read_file(file_id, read_url)

    @staticmethod
    def _write_data(file_content, write_location):
        response = requests.put(write_location, files={'file': BytesIO(file_content)})
        if not response.ok:
            raise FileServiceException("failed to save image")

    def _create_location(self):
        url = self._storage_url + "dir/assign"
        response_creation = requests.post(url)
        if not response_creation.ok:
            raise FileServiceException("failed to save image. Id allocation issue")
        json = response_creation.json()
        fid = json['fid']
        url = json['publicUrl']
        write_location = self.protocol + url + self.url_delimiter + fid
        return fid, write_location

    def _read_file(self, file_id, read_url):
        response = requests.get(self.protocol + read_url + self.url_delimiter + file_id)
        if not response.ok:
            raise FileNotFoundException("File with id '{}' is missing in a storage '{}'".format(file_id, read_url))
        return response.content

    def _find_file_location(self, file_id):
        if not isinstance(file_id, str):
            raise WrongFileId()

        response = requests.get(self._storage_url + "/dir/lookup?volumeId=" + file_id)
        if not response.ok:
            raise FileNotFoundException("File with id '{}' is not found".format(file_id))

        return self._decode_location(file_id, response)

    @staticmethod
    def _decode_location(file_id, response):
        try:
            read_url = response.json()["locations"][0]["publicUrl"]
        except Exception:
            raise FileServiceException("Unable to parse index for file '{}'".format(file_id))
        return read_url
