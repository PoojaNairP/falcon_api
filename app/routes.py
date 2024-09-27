from app.user_resource import UserResource

def setup_routes(app):
    app.add_route('/users', UserResource())