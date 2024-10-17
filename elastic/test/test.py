import json
import unittest
from unittest.mock import patch
import falcon
from falcon import testing
from elastic.app.user_resource import UserResource, PostUser, GetUser
from elastic.app.elastic_repository import ElasticRepository


class TestPostUser(unittest.TestCase):

    def setUp(self):
        self.app = falcon.App()
        self.user_resource = UserResource()
        self.post_user=PostUser()
        self.app.add_route('/user', self.post_user)
        self.client = testing.TestClient(self.app)

    @patch.object(ElasticRepository, 'add_user')
    @patch.object(ElasticRepository, 'add_to_json_file')
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

    @patch.object(ElasticRepository, 'add_user')
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

    @patch.object(ElasticRepository, 'get_user')
    def test_on_get_user_found(self, mock_get_user):
        mock_get_user.return_value = {'email': 'test@example.com', 'name': 'Test User'}
        result = self.client.simulate_get('/user/test@example.com')
        self.assertEqual(result.status, falcon.HTTP_200)
        self.assertEqual(result.json['email'], 'test@example.com')
        self.assertEqual(result.json['name'], 'Test User')

    @patch.object(ElasticRepository, 'get_user')
    def test_on_get_user_not_found(self, mock_get_user):
        mock_get_user.return_value = None
        result = self.client.simulate_get('/user/test@example.com')
        self.assertEqual(result.status, falcon.HTTP_400)
        self.assertEqual(result.json['statusMessage'], 'No user found with given email')


    @patch.object(ElasticRepository, 'get_user')
    def test_on_get_invalid_email(self, mock_get_user):
        mock_get_user.return_value = None
        result = self.client.simulate_get('/user/test')
        self.assertEqual(result.status, falcon.HTTP_400)
        self.assertEqual(result.json['statusMessage'], 'Email is not valid')


if __name__ == '__main__':
    unittest.main()





