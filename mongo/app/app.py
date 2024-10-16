import falcon

from mongo.app.routes import setup_routes


app=falcon.App()

setup_routes(app)