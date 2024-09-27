import re

class UserModel:

    def __init__(self, data):
        self.name = data.get('name')
        self.email = data.get('email')
        self.age = data.get('age')
        self.validate_fields(data)


    def validate_fields(self,data):
        valid_keys = {"name", "email", "age"}
        extra_keys = set(data.keys()) - valid_keys
        if extra_keys:
            raise ValueError(f"Unexpected fields: {', '.join(extra_keys)}")

        if type(self.age)!=int:
            raise ValueError("Integer Value expected")

        if self.age<1:
            raise ValueError(f"Age can't be less than 0")


        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',self.email):
            raise ValueError("Email is not valid")




