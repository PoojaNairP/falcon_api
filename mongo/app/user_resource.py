import json
import re
import falcon

from mongo.app.model import UserModel
from mongo.app.mongo_repository import MongoRepository
from mongo.app.response import GenericResponse


class UserResource:
    def __init__(self):
        self.mongorepo=MongoRepository()


class PostUser(UserResource):
    def on_post(self, req, res):
        try:
            data_stream = req.media
            UserModel(data_stream)
            response=self.mongorepo.add_user(req.media)
            if response:
                res.media = json.loads(GenericResponse(falcon.HTTP_201,"Successfully Created").to_json())
                res.status = falcon.HTTP_201

        except Exception as ex:
            res.status = falcon.HTTP_400
            res.media = res.media = json.loads(GenericResponse(falcon.HTTP_400,str(ex)).to_json())

class GetUser(UserResource):
    def on_get(self,req,res,email):
        try:
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',email):
                raise ValueError("Email is not valid")

            user=self.mongorepo.get_user(email)
            if not user:
                raise falcon.HTTPBadRequest(title="No user found with given email")

            res.status=falcon.HTTP_200
            res.media=user

        except falcon.HTTPBadRequest as ex:
            res.status = falcon.HTTP_400
            res.media = json.loads(GenericResponse(falcon.HTTP_400,str(ex.title)).to_json())

        except Exception as ex:
            res.status = falcon.HTTP_400
            res.media = json.loads(GenericResponse(falcon.HTTP_400,str(ex)).to_json())


