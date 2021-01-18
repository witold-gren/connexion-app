#!/usr/bin/env python3
import connexion

from http import HTTPStatus
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError

from commands import run_unitest, import_data, check_migration, check_db_connection
from config import app_config
from extensions import db, migrate, PathLocationResolver


def create_app(config_name):
    """
    Create and configure an instance of the Flask application
    :param config_object: The configuration object to use.
    """
    config_object = app_config[config_name]
    connexion_app = connexion.App(__name__,
                                  options={
                                      "serve_spec": config_object.SERVE_SPEC,
                                      "swagger_ui": config_object.SWAGGER_UI,
                                  })
    flask_app = connexion_app.app

    # configure flask with environment variables
    flask_app.config.from_object(config_object)

    # initialize API
    connexion_app.add_api('swagger.yml',
                          resolver=PathLocationResolver(prefix='api'),
                          strict_validation=True,
                          validate_responses=True)

    # register exception handler
    register_error_handlers(flask_app)

    # initialize extension
    with flask_app.app_context():
        register_extensions(flask_app)

    # initialize extra command line
    register_commands(flask_app)

    return connexion_app


def register_extensions(app):
    """register data base and migrations object"""
    db.init_app(app)
    migrate.init_app(app, db)


def register_error_handlers(app):

    @app.errorhandler(AssertionError)
    def handle_sql_alchemy_error(error):
        db.session.rollback()
        resp = jsonify({"detail": str(error),
                        "status": HTTPStatus.BAD_REQUEST,
                        "title": "Bad Request",
                        "type": "validation"})
        resp.status_code = HTTPStatus.BAD_REQUEST
        return resp

    @app.errorhandler(SQLAlchemyError)
    def handle_sql_alchemy_error(error):
        db.session.rollback()
        resp = jsonify({"detail": str(error),
                        "status": HTTPStatus.INTERNAL_SERVER_ERROR,
                        "title": "Internal Server Error",
                        "type": "orm"})
        resp.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        return resp

    @app.errorhandler(HTTPStatus.NOT_FOUND)
    def handle_404(error):
        resp = jsonify({"detail": str(error),
                        "status": HTTPStatus.NOT_FOUND,
                        "title": "Not Found",
                        "type": "http"})
        resp.status_code = HTTPStatus.NOT_FOUND
        return resp

    @app.errorhandler(HTTPStatus.UNAUTHORIZED)
    def handle_401(error):
        resp = jsonify({"detail": str(error),
                        "status": HTTPStatus.UNAUTHORIZED,
                        "title": "Unauthorized",
                        "type": "http"})
        resp.status_code = HTTPStatus.UNAUTHORIZED
        return resp

    @app.errorhandler(HTTPStatus.FORBIDDEN)
    def handle_403(error):
        resp = jsonify({"detail": str(error),
                        "status": HTTPStatus.FORBIDDEN,
                        "title": "Forbidden",
                        "type": "http"})
        resp.status_code = HTTPStatus.FORBIDDEN
        return resp


def register_commands(app):
    """Register extra command"""
    app.cli.add_command(run_unitest)
    app.cli.add_command(import_data)
    app.cli.add_command(check_migration)
    app.cli.add_command(check_db_connection)
