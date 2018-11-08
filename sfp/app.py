import falcon
from sfp.routes import define_routes

app = falcon.API()
define_routes(app)
