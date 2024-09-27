import json
import pytest
from falcon import testing
import falcon
from app.model import UserModel
from app.mongo_repository import MongoRepository
from app.user_resource import UserResource

@pytest.fixture
def client():
    app = falcon.App()
    user_resource = UserResource()
    app.add_route('/user', user_resource)
    return testing.TestClient(app)

def test_unexpected_fields():
    data = {"name": "Test User", "email": "test@example.com", "age": 25, "extra_field": "value"}
    with pytest.raises(ValueError, match="Unexpected fields: extra_field"):
        UserModel(data)

def test_invalid_age_type():
    data = {"name": "Test User", "email": "test@example.com", "age": "twenty-five"}
    with pytest.raises(ValueError, match="Integer Value expected"):
        UserModel(data)

def test_age_less_than_one():
    data = {"name": "Test User", "email": "test@example.com", "age": 0}
    with pytest.raises(ValueError, match="Age can't be less than 0"):
        UserModel(data)

def test_invalid_email_format():
    data = {"name": "Test User", "email": "invalid-email", "age": 25}
    with pytest.raises(ValueError, match="Email is not valid"):
        UserModel(data)

def test_on_post_user_exists(client, mocker):
    mocker.patch.object(MongoRepository, 'get_user', return_value={'email': 'test@example.com'})
    body = json.dumps({'email': 'test@example.com', 'name': 'Test User', 'age': 25})
    result = client.simulate_post('/user', body=body)
    assert result.status == falcon.HTTP_400
    assert 'Email already exists' in result.json["error"]

def test_on_post_user_added(client, mocker):
    mocker.patch.object(MongoRepository, 'get_user', return_value=None)
    mocker.patch.object(MongoRepository, 'add_user', return_value='User added successfully')
    body = json.dumps({"email": "newuser@example.com", "name": "New User", "age": 30})
    result = client.simulate_post('/user', body=body)
    assert result.status == falcon.HTTP_200
    assert result.json['message'] == 'User added successfully'

def test_on_get_user_found(client, mocker):
    mocker.patch.object(MongoRepository, 'get_user', return_value={'email': 'test@example.com', 'name': 'Test User'})
    result = client.simulate_get('/user', params={'email': 'test@example.com'})
    assert result.status == falcon.HTTP_200
    assert result.json['email'] == 'test@example.com'
    assert result.json['name'] == 'Test User'

def test_on_get_user_not_found(client, mocker):
    mocker.patch.object(MongoRepository, 'get_user', return_value=None)
    result = client.simulate_get('/user', params={'email': 'nonexistent@example.com'})
    assert result.status == falcon.HTTP_400 # Expecting 404 for not found
    assert 'No user found with given email' in result.json['message']



