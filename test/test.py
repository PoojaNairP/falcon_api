import json
import unittest
from unittest.mock import patch, Mock
import falcon
from falcon import testing
from marshmallow import ValidationError
from app.model import UserModel
from app.user_resource import UserResource
from app.mongo_repository import MongoRepository


class TestUserResource(unittest.TestCase):

    def setUp(self):
        self.app = falcon.App()
        self.user_resource = UserResource()
        self.app.add_route('/user', self.user_resource)
        self.client = testing.TestClient(self.app)

    def tearDown(self):
        self.user_resource.mongorepo.close()

    @patch.object(MongoRepository, 'add_user')
    @patch.object(UserModel, 'load')
    def test_on_post_user_success(self, mock_load, mock_add_user):
        mock_load.return_value = {}
        mock_add_user.return_value = True

        body = json.dumps({"email": "test@example.com", "name": "Test User", "age": 25})
        result = self.client.simulate_post('/user', body=body, content_type='application/json')

        self.assertEqual(result.status, falcon.HTTP_201)
        self.assertEqual(result.json['message'], 'Successfully created')

    @patch.object(UserModel, 'load')
    def test_on_post_user_validation_error(self, mock_load):
        mock_load.side_effect = ValidationError({'email': ['Invalid email format']})

        body = json.dumps({"email": "invalid-email", "name": "Test User"})
        result = self.client.simulate_post('/user', body=body, content_type='application/json')

        self.assertEqual(result.status, falcon.HTTP_400)
        self.assertIn('errors', result.json)

    @patch.object(MongoRepository, 'add_user')
    @patch.object(UserModel, 'load')
    def test_on_post_email_exists(self, mock_load, mock_add_user):
        mock_load.return_value = {}
        mock_add_user.side_effect = Exception("Email already exists")

        body = json.dumps({"email": "test@example.com", "name": "Test User", "age": 25})
        result = self.client.simulate_post('/user', body=body, content_type='application/json')

        self.assertEqual(result.status, falcon.HTTP_400)
        self.assertIn('error', result.json)

    @patch.object(UserModel,'load')
    def test_on_post_validation_error(self,mock_load):
        mock_load.side_effect=ValidationError("Missing values")
        body = json.dumps({"email": "test@example.com", "name": "Test User","age": 18,"id":1})
        result = self.client.simulate_post('/user', body=body, content_type='application/json')

        self.assertEqual(result.status, falcon.HTTP_400)
        self.assertIn('errors', result.json)



if __name__ == '__main__':
    unittest.main()





