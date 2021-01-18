import sys
import csv
import unittest
from pathlib import Path

import click
import sqlalchemy
import psycopg2
from flask import current_app
from flask.cli import with_appcontext
from alembic.script import ScriptDirectory
from alembic.config import Config
from alembic.runtime.migration import MigrationContext

import models
from extensions import db, create_testing_db


@click.command(name='test')
@click.option('-v', '--verbose', count=True, default=1)
@click.option('-p', '--path', type=click.Path(exists=True), default='tests')
@with_appcontext
def run_unitest(verbose, path):
    """Run the tests."""
    create_testing_db()
    suite = unittest.TestLoader().discover(path)
    unittest.TextTestRunner(verbosity=verbose).run(suite)


@click.command(name='check_migration')
@with_appcontext
def check_migration():
    """Check that current app has applied all migrations."""
    config = Config()
    config.set_main_option("script_location", "migrations")
    script = ScriptDirectory.from_config(config)
    head_revision = script.get_current_head()
    engine = sqlalchemy.create_engine(current_app.config.get('SQLALCHEMY_DATABASE_URI'))
    conn = engine.connect()
    context = MigrationContext.configure(conn)
    current_rev = context.get_current_revision()
    if head_revision != current_rev:
        print(f'Upgrade the database. head_revision: {head_revision}. current_rev: {current_rev}')
        sys.exit(-1)
    sys.exit(0)


@click.command(name='check_db_connection')
@with_appcontext
def check_db_connection():
    """Check that current app has applied all migrations."""
    try:
        psycopg2.connect(current_app.config.get('SQLALCHEMY_DATABASE_URI'))
    except psycopg2.OperationalError:
        sys.exit(-1)
    sys.exit(0)


@click.command()
@click.argument('filename', type=click.Path(exists=True))
@with_appcontext
def import_data(filename):
    """Import data from csv file."""
    with Path(filename).open() as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)  # skip header
        buffer, count = [], 0
        for row in csv_reader:
            count += 1
            survived, pclass, name, sex, age, siblings, parents, fare = row
            buffer.append(models.Person(
                survived=bool(survived), passenger_class=int(pclass),
                name=name, sex=sex, age=int(float(age)),
                siblings_or_spouses_aboard=int(float(siblings)),
                parents_or_children_aboard=int(parents),
                fare=float(fare)))
            if len(buffer) % 10000 == 0:
                print(f'Imported: {count} items')
                db.session.bulk_save_objects(buffer)
                db.session.commit()
                buffer = []
        if buffer:
            print(f'Imported: {count} items')
            db.session.bulk_save_objects(buffer)
            db.session.commit()
