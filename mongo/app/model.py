import re

class UserModel:

    def __init__(self, data):
        self.name = data.get('name')
        self.email = data.get('email')
        self.age = data.get('age')
        self.validate_fields(data)

    def validate_fields(self, data):
        valid_keys = {"name", "email", "age"}

        no_key = valid_keys - set(data.keys())
        if no_key:
            raise ValueError(f"Required fields not present: {', '.join(no_key)}")

        extra_keys = set(data.keys()) - valid_keys
        if extra_keys:
            raise ValueError(f"Unexpected fields: {', '.join(extra_keys)}")

        if type(self.name) != str:
            raise ValueError("Name has to be a String")

        if len(self.name) < 1:
            raise ValueError("Name can't be null")

        if type(self.age) != int:
            raise ValueError("Integer Value expected")

        if self.age < 1:
            raise ValueError(f"Invalid Age provided")

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', self.email):
            raise ValueError("Email is not valid")






