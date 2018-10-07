
import ConfigParser  
from flask_sqlalchemy import SQLAlchemy
from database import DB
from flask import jsonify, request
import json
from index import init
from routes.route_path_general import route_path_general
from flask_swagger import swagger
def create_app():
    app = init()
    mysql = DB(app)

    app.register_blueprint(route_path_general, url_prefix='/api')

    @app.after_request
    def add_header(response):
        return response

    @app.errorhandler(400)
    def bad_request(e):
        logging.error(e)
        return response_with(resp.BAD_REQUEST_400)

    @app.errorhandler(500)
    def server_error(e):
        logging.error(e)
        return response_with(resp.SERVER_ERROR_500)

    @app.errorhandler(404)
    def not_found(e):
        logging.error(e)
        return response_with(resp.NOT_FOUND_HANDLER_404)

    @app.route("/api/spec")
    def spec():
        swag = swagger(app)
        swag['info']['version'] = "1.0"
        swag['info']['title'] = "Inventory Management App"
        return jsonify(swag)


    return app