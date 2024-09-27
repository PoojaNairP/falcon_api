import falcon


from app.mongo_repository import MongoRepository
from app.routes import setup_routes

app=falcon.App()

setup_routes(app)