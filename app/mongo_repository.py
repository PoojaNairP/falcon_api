from pymongo import MongoClient

class MongoRepository:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['userdb']
        self.collection = self.db['users']

    def add_user(self, user_data):
        result=self.collection.insert_one(user_data)
        return "Successfully added"

    def get_user(self, email):
        try:
            return self.collection.find_one({'email': email}, {'_id': 0})
        except Exception as e:
            print(f"Error retrieving user details: {e}")
            return None