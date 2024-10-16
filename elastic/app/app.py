import falcon

from elastic.app.routes import setup_routes


app=falcon.App()

setup_routes(app)