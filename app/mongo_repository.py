from pymongo import MongoClient

class MongoRepository:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['userdb']
        self.collection = self.db['users']


    def get_user(self, user_id):
        try:
            return self.collection.find_one({'_id': int(user_id)})  # Convert to int
        except Exception as e:
            print(f"Error retrieving user: {e}")
            return None

    def add_user(self, user_data):
        result=self.collection.insert_one(user_data) # Add a user
        return "Successfully added"
