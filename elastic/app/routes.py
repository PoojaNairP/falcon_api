from elastic.app.user_resource import PostUser, GetUser


def setup_routes(app):
    app.add_route('/users', PostUser())
    app.add_route('/users/{email}', GetUser())