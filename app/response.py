import json

class GenericResponse:
    def __init__(self, code, msg):
        self.statusCode = code
        self.statusMessage = msg

    def to_json(self):
        return json.dumps({"statusCode": self.statusCode, "statusMessage": self.statusMessage},indent=4)


