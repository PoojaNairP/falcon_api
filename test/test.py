import json
import unittest
from unittest.mock import MagicMock, patch
import falcon
from falcon import testing
from marshmallow import ValidationError
from app.model import UserModel
from app.user_resource import UserResource
from app.mongo_repository import MongoRepository
from pymongo.errors import DuplicateKeyError


class TestUserResource(unittest.TestCase):

    def setUp(self):
        self.app = falcon.App()
        self.user_resource = UserResource()
        self.app.add_route('/user', self.user_resource)
        self.app.add_route('/user/{email}', self.user_resource)
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

    @patch.object(MongoRepository, 'get_user')
    def test_on_get_user_found(self, mock_get_user):
        mock_get_user.return_value = {'email': 'test@example.com', 'name': 'Test User'}

        result = self.client.simulate_get('/user/test@example.com')

        self.assertEqual(result.status, falcon.HTTP_200)
        self.assertEqual(result.json['email'], 'test@example.com')
        self.assertEqual(result.json['name'], 'Test User')

    @patch.object(MongoRepository, 'get_user')
    def test_on_get_user_not_found(self, mock_get_user):
        mock_get_user.return_value = None

        result = self.client.simulate_get('/user/test@example.com')

        self.assertEqual(result.status, falcon.HTTP_400)
        self.assertIn('message', result.json)
        self.assertEqual(result.json['message'], 'No user found with given email')

    @patch.object(MongoRepository, 'get_user')
    def test_on_get_invalid_email(self, mock_get_user):
        mock_get_user.return_value = None

        result = self.client.simulate_get('/user/test')

        self.assertEqual(result.status, falcon.HTTP_400)
        self.assertIn('error', result.json)
        self.assertEqual(result.json['error'], 'Email is not valid')



class TestMongoRepository(unittest.TestCase):

    @patch('app.mongo_repository.MongoClient')
    def setUp(self, mock_mongo_client):
        self.mock_client = mock_mongo_client.return_value
        self.mock_db = self.mock_client['test_database']
        self.mock_collection = self.mock_db['users']
        self.repository = MongoRepository()
        self.repository.collection = self.mock_collection

    def test_add_user_success(self):
        user_data = {'email': 'test@example.com', 'name': 'Test User'}
        self.mock_collection.insert_one = MagicMock(return_value=True)

        result = self.repository.add_user(user_data)

        self.assertTrue(result)
        self.mock_collection.insert_one.assert_called_once_with(user_data)

    def test_add_user_duplicate_key(self):
        user_data = {'email': 'test@example.com', 'name': 'Test User'}
        self.mock_collection.insert_one.side_effect = DuplicateKeyError("Email already exists")

        with self.assertRaises(Exception) as context:
            self.repository.add_user(user_data)

        self.assertEqual(str(context.exception), "Email already exists")

    def test_get_user_found(self):
        user_data = {'email': 'test@example.com', 'name': 'Test User'}
        self.mock_collection.find_one = MagicMock(return_value=user_data)

        user = self.repository.get_user('test@example.com')

        self.assertEqual(user, user_data)
        self.mock_collection.find_one.assert_called_once_with({'email': 'test@example.com'},{'_id':0})

    def test_get_user_not_found(self):
        self.mock_collection.find_one = MagicMock(return_value=None)

        user = self.repository.get_user('nonexistent@example.com')

        self.assertIsNone(user)
        self.mock_collection.find_one.assert_called_once_with({'email': 'nonexistent@example.com'},{'_id':0})


if __name__ == '__main__':
    unittest.main()





