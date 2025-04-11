import json


def generate_error(err_cls, message: str | dict | list):
    message = json.dumps({"error": message})
    return err_cls(text=message, content_type="application/json")
