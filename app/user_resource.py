import re
from marshmallow import ValidationError
import falcon

from app.model import UserModel
from app.mongo_repository import MongoRepository


class UserResource:
    def __init__(self):
        self.mongorepo=MongoRepository()

    def on_post(self, req, res):
        try:
            data_stream = req.media
            #print(data_stream)

            schema=UserModel()
            schema.load(data_stream)

            response=self.mongorepo.add_user(req.media)

            if response:

                res.media = {"message":"Successfully created"}
                res.status = falcon.HTTP_201

        except ValidationError as err:
            res.status = falcon.HTTP_400
            res.media = {'errors': err.messages}

        except Exception as e:
            res.status = falcon.HTTP_400
            res.media = {"error": str(e)}

    def on_get(self,req,res,email):
        try:
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


