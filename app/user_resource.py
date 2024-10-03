import json
import re

import falcon

from app.model import UserModel
from app.mongo_repository import MongoRepository


class UserResource:
    def __init__(self):
        self.mongorepo=MongoRepository()

    def on_post(self, req, res):
        try:
            data_stream = req.media
            print(data_stream)
            UserModel(req.media)
            response=self.mongorepo.add_user(req.media)
            if response:
                data_to_save = {k: v for k, v in data_stream.items() if k != '_id'}
                self.add_to_json_file(data_to_save)
                res.media = {"message":"Successfully created"}
                res.status = falcon.HTTP_200

        except falcon.HTTPBadRequest as e:
            res.status = falcon.HTTP_400
            res.media = {"error": str(e.title)}

        except ValueError as e:
            res.media={"error": str(e)}
            res.status = falcon.HTTP_400
        except Exception as e:
            res.status = falcon.HTTP_400
            res.media = {"error": str(e)}

    def on_get(self,req,res):
        try:
            email=req.get_param('email')
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',email):
                raise ValueError("Email is not valid")
            user=self.mongorepo.get_user(email)
            if not user:
                raise falcon.HTTPBadRequest(title="No user found with given email")
            res.status=falcon.HTTP_200
            res.media=user

        except falcon.HTTPBadRequest as e:
            res.status = falcon.HTTP_400
            res.media = {"message": str(e.title)}

        except Exception as e:
            res.status = falcon.HTTP_400
            res.media = {"error": str(e)}


    def add_to_json_file(self,data_stream):
        try:
            filepath = 'user_data.json'
            with open(filepath, 'r') as file:
                data = json.load(file)
            data.append(data_stream)
            with open(filepath, 'w') as file:
                json.dump(data, file, indent=4)

        except Exception as e:
            print(e)


