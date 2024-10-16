import json
import unittest
from unittest.mock import MagicMock, patch
import falcon
from falcon import testing
from elastic.app.user_resource import UserResource, PostUser, GetUser
from elastic.app.mongo_repository import MongoRepository
from pymongo.errors import DuplicateKeyError


class TestPostUser(unittest.TestCase):

    def setUp(self):
        self.app = falcon.App()
        self.user_resource = UserResource()
        self.post_user=PostUser()
        self.app.add_route('/user', self.post_user)
        self.client = testing.TestClient(self.app)

    def tearDown(self):
        self.user_resource.mongorepo.close()

    @patch.object(MongoRepository, 'add_user')
    @patch.object(MongoRepository,'add_to_json_file')
    def test_on_post_user_success(self, mock_add_user,mock_add_to_json_file):
        mock_add_user.return_value = True
        mock_add_to_json_file.return_value=True
        body = json.dumps({"email": "test@example.com", "name": "Test User", "age": 25})
        result = self.client.simulate_post('/user', body=body, content_type='application/json')
        self.assertEqual(result.status, falcon.HTTP_201)
        self.assertEqual(result.json['statusMessage'], 'Successfully Created')

    def test_on_post_user_MissingField(self):
        body = json.dumps({"email": "test@example.com", "name": "Test User"})
        result = self.client.simulate_post('/user', body=body, content_type='application/json')
        self.assertEqual(result.status, falcon.HTTP_400)
        self.assertEqual(result.json['statusMessage'],"Required fields not present: age")

    def test_on_post_user_ExtraField(self):
        body = json.dumps({"email": "test@example.com", "name": "Test User", "age": 45, "extra": "extra field"})
        result = self.client.simulate_post('/user', body=body, content_type='application/json')
        self.assertEqual(result.status, falcon.HTTP_400)
        self.assertEqual(result.json['statusMessage'],"Unexpected fields: extra")

    def test_on_post_user_InvalidName(self):
        body = json.dumps({"email": "test@example.com", "name": "", "age": 45})
        result = self.client.simulate_post('/user', body=body, content_type='application/json')
        self.assertEqual(result.status, falcon.HTTP_400)
        self.assertEqual(result.json['statusMessage'],"Name can't be null")

        body = json.dumps({"email": "test@example.com", "name": 123, "age": 45})
        result = self.client.simulate_post('/user', body=body, content_type='application/json')
        self.assertEqual(result.status, falcon.HTTP_400)
        self.assertEqual(result.json['statusMessage'], "Name has to be a String")

    def test_on_post_user_InvalidAge(self):
        body = json.dumps({"email": "test@example.com", "name": "Rohit", "age": "invalid"})
        result = self.client.simulate_post('/user', body=body, content_type='application/json')
        self.assertEqual(result.status, falcon.HTTP_400)
        self.assertEqual(result.json['statusMessage'],"Integer Value expected")

        body = json.dumps({"email": "test@example.com", "name": "Rohit", "age": -45})
        result = self.client.simulate_post('/user', body=body, content_type='application/json')
        self.assertEqual(result.status, falcon.HTTP_400)
        self.assertEqual(result.json['statusMessage'], "Invalid Age provided")

    def test_on_post_user_InvalidEmail(self):
        body = json.dumps({"email": "test", "name": "Rohit", "age": 45})
        result = self.client.simulate_post('/user', body=body, content_type='application/json')
        self.assertEqual(result.status, falcon.HTTP_400)
        self.assertEqual(result.json['statusMessage'],"Email is not valid")

    @patch.object(MongoRepository, 'add_user')
    def test_on_post_email_exists(self, mock_add_user):
        mock_add_user.side_effect = Exception("Email already exists")
        body = json.dumps({"email": "test@example.com", "name": "Test User", "age": 25})
        result = self.client.simulate_post('/user', body=body, content_type='application/json')
        self.assertEqual(result.status, falcon.HTTP_400)
        self.assertEqual(result.json['statusMessage'],"Email already exists")


class TestGetUser(unittest.TestCase):

    def setUp(self):
        self.app = falcon.App()
        self.user_resource = UserResource()
        self.get_user = GetUser()
        self.app.add_route('/user/{email}', self.get_user)
        self.client = testing.TestClient(self.app)

    def tearDown(self):
        self.user_resource.mongorepo.close()

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
        self.assertEqual(result.json['statusMessage'], 'No user found with given email')


    @patch.object(MongoRepository, 'get_user')
    def test_on_get_invalid_email(self, mock_get_user):
        mock_get_user.return_value = None
        result = self.client.simulate_get('/user/test')
        self.assertEqual(result.status, falcon.HTTP_400)
        self.assertEqual(result.json['statusMessage'], 'Email is not valid')



class TestMongoRepository(unittest.TestCase):

    @patch('elastic.app.mongo_repository.MongoClient')
    def setUp(self, mock_mongo_client):
        self.mock_client = mock_mongo_client.return_value
        self.mock_db = self.mock_client['test_database']
        self.mock_collection = self.mock_db['users']
        self.repository = MongoRepository()
        self.repository.collection = self.mock_collection

    @patch.object(MongoRepository,'add_to_json_file')
    def test_add_user_success(self,mock_add_to_json_file):
        mock_add_to_json_file.return_value = True
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

    def test_get_user_exception(self):
        self.mock_collection.find_one = MagicMock(side_effect=Exception("Database connection error"))
        user = self.repository.get_user('nonexistent@example.com')
        self.assertIsNone(user)
        self.mock_collection.find_one.assert_called_once_with({'email': 'nonexistent@example.com'}, {'_id': 0})

if __name__ == '__main__':
    unittest.main()





