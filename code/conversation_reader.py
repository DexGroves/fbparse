import json


class ConversationReader(object):
    """Read a conversation."""

    def __init__(self, path):
        pass

    @staticmethod
    def read_json_to_list(path):
        """Read Facebook JSON and return list."""
        with open(path) as data_file:
            data = json.load(data_file)
        return data
