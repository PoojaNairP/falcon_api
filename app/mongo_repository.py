import json

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

class MongoRepository:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['userdb']
        self.collection = self.db['users']
        self.collection.create_index([("email", 1)], unique=True)

    def close(self):
        self.client.close()

    def add_user(self, user_data):
        try:
            result=self.collection.insert_one(user_data)
            data_to_save = {k: v for k, v in user_data.items() if k != '_id'}
            self.add_to_json_file(data_to_save)
            return True
        except DuplicateKeyError:
            raise Exception("Email already exists")


    def get_user(self, email):
        try:
            return self.collection.find_one({'email': email}, {'_id': 0})

        except Exception as e:
            print(f"Error retrieving user details: {e}")
            return None


    def add_to_json_file(self, data_stream):
        filepath = 'user_data.json'
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = []
        except json.JSONDecodeError:
            data = []

        data.append(data_stream)

        try:
            with open(filepath, 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            print(f"An error occurred while writing to the file: {e}")