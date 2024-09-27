import json

import falcon

from app.model import UserModel
from app.mongo_repository import MongoRepository


class UserResource:
    def __init__(self):
        self.mongorepo=MongoRepository()

    def on_post(self, req, res):
        try:
            data_stream = json.loads(req.stream.read())
            UserModel(data_stream)
            self.add_to_json_file(data_stream)
            res.media = {"message":self.mongorepo.add_user(data_stream)}
            res.status = falcon.HTTP_200


        except Exception as e:
            res.status = falcon.HTTP_400
            res.media = {"error": str(e)}

    def add_to_json_file(self,data_stream):
        try:
            filepath = 'user_data.json'
            with open(filepath, 'r') as file:
                data = list(json.load(file))
            data.append(data_stream)
            with open(filepath, 'w') as file:
                json.dump(data, file, indent=4)

        except Exception as e:
            print(e)


