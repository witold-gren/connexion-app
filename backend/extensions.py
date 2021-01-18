import logging
import sqlalchemy
from flask import current_app
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from connexion.resolver import Resolver


db = SQLAlchemy()
migrate = Migrate()
logger = logging.getLogger('alembic')


def create_testing_db():
    """Create DB for testing"""
    engine = sqlalchemy.create_engine(current_app.config.get('SQLALCHEMY_DATABASE_URI'))
    conn = engine.connect()
    conn.connection.connection.set_isolation_level(0)
    try:
        conn.execute(f"CREATE DATABASE test_{current_app.config.get('DB_NAME')}")
        logger.info(f"Created testing database `test_{current_app.config.get('DB_NAME')}`")
    except sqlalchemy.exc.ProgrammingError:
        logger.info(f"Database for testing `test_{current_app.config.get('DB_NAME')}` exist.")
    conn.connection.connection.set_isolation_level(1)
    conn.close()


class PathLocationResolver(Resolver):
    """ Custom patch to fing module and function in selected folder"""

    def __init__(self, *args, **kwargs):
        self.prefix = kwargs.pop('prefix', None)
        super().__init__(*args, **kwargs)

    @staticmethod
    def default_resolve_operation_id(operation):
        operation_id = operation.operation_id
        router_controller = operation.router_controller
        if operation.router_controller is None:
            return operation_id
        return '{}.{}'.format(router_controller, operation_id)

    def resolve_operation_id(self, operation):
        method = self.default_resolve_operation_id(operation)
        if operation.operation_id and self.prefix:
            method = '{}.{}'.format(self.prefix, method)
        return method
