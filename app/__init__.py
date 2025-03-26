from flask import Flask
from . import routes, authentication
from .configuration import configuration

def create_app():
    app = Flask(__name__,
        static_url_path=f'/{configuration.context_path.strip("/")}/static' if configuration.context_path else '/static',
        template_folder='./templates',
        static_folder='./static')
    authentication.init_app(app)
    routes.add_routes(app)
    return app


linktiles = create_app()
