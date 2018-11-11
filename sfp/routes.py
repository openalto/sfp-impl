from sfp.entries import QueryEntry, PeerRegisterEntry, PathQueryEntry


def define_routes(app):
    app.add_route('/query', QueryEntry())
    app.add_route('/register', PeerRegisterEntry())
    app.add_route('/path-query', PathQueryEntry())