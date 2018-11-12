import os
import json


class Data:
    def __init__(self, config_file_path=None):
        if config_file_path is None:
            config_file_path = os.environ["HOME"] + "/sc18.json"

        self.domain_data = {}
        self._read_config_file(config_file_path)

    def _read_config_file(self, config_file_path):
        self.domain_data = json.load(open(config_file_path))


data = Data()
