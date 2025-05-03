'''
Data base storing the events created by the app
'''
import sqlite3
from datetime import datetime

import click
from flask import current_app, g

def init_app(app):
  app.teardown_appcontext(clode_db)
  app.cli.add_command(init_db_command)

'''
@usage: use when starting server
@desc: opens database and loads previous data
'''
def init_db():
    db = get_db()

    with current_app.open_resource('events.sql') as f:
      db.executescript(f.read().decode('utf-8'))

'''
@usage: Use to access the database
@desc: Validates if the database for the events and users exists, in the case it doesn't it will create it.
'''
def get_db():
  if 'db' not in g:
    g.db = sqlite3.connect(
      current_app.config['DATABASE'],
      detect_types=sqlite3.PARSE_DECLTYPES
    )
    g.db.row_factory=sqlite3.Row
  return g.db

'''
@usage: Use when shutting down the server
@desc: Closes the database
'''
def clode_db(e=None):
  db = g.pop('db', None)

  if db is not None:
    db.close()

@click.command('init-db')
def init_db_command():
  init_db()
  click.echo('Initialized the database.')

sqlite3.register_converter(
  "timestamp", lambda v:datetime.fromisoformat(v.decode())
)