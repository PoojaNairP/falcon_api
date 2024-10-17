import json
from elasticsearch import Elasticsearch, ConflictError


class ElasticRepository:
    def __init__(self):
        self.es = Elasticsearch(['http://localhost:9200'], http_auth=('elastic', 'kyXqM*IZV0Y6kNAcT24P'))

    def add_user(self, user_data):
        try:
            self.es.index(index='users',id=user_data['email'],document=user_data,op_type='create')
            self.add_to_json_file(user_data)
            return True
        except ConflictError:
            raise Exception("Email already exists")


    def get_user(self, email):
        try:
             response=self.es.search(index='users',query={'term': {'email.keyword': email}})
             if not response['hits']['hits']:
                 return False
             return response['hits']['hits'][0]['_source']

        except Exception as e:
            print(f"Error retrieving user details: {e}")
            return None


    def add_to_json_file(self, data_stream):
        filepath = 'elastic/user_data.json'
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
            return True
        except Exception as e:
            print(f"An error occurred while writing to the file: {e}")