from sfp.entries import QueryEntry, PeerRegisterEntry


def define_routes(app):
    app.add_route('/query', QueryEntry())
    app.add_route('/register', PeerRegisterEntry())
