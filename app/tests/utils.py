import json


def get_url_with_query_string(url="", **kwargs):
    return url + "?" + "&".join([f"{key}={json.dumps(value)}" for key, value in kwargs.items() if value is not None])
