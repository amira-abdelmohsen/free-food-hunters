'''
Data base storing the events created by the app
'''
import sqlite3
from datetime import datetime

import click
from flask import current_app, g

def init_app(app):
  app.teardown_appcontext(close_db)
  app.cli.add_command(init_db_command)

'''
@usage: use when starting server
@desc: opens database and loads previous data
'''
def init_db():
    db = get_db()

    with current_app.open_resource('events.sql') as f:
      db.executescript(f.read().decode('utf8'))

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
def close_db(e=None):
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

def insert_event(data):
    db = get_db()
    db.execute("""
        INSERT INTO events (author_email, title, description, location, pickup_time, time_remaining, allergies)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data["author_email"],
        data["title"],
        data["description"],
        data["location"],
        data["pickup_time"],
        data["time_remaining"],
        data["allergies"]
    ))
    db.commit()

def get_events_by_author(email):
    db = get_db()
    return db.execute("SELECT * FROM events WHERE author_email = ?", (email,)).fetchall()

def delete_event(event_id):
    db = get_db()
    db.execute("DELETE FROM events WHERE id = ?", (event_id,))
    db.commit()

from datetime import timedelta

def delete_expired_events():
    db = get_db()
    now = datetime.now()
    rows = db.execute("SELECT id, created_at, time_remaining FROM events").fetchall()

    for row in rows:
        try:
            created = row["created_at"] if isinstance(row["created_at"], datetime) else datetime.fromisoformat(str(row["created_at"]))
            delta = parse_time_remaining(row["time_remaining"])
            if created + delta <= now:
                db.execute("DELETE FROM events WHERE id = ?", (row["id"],))
        except Exception as e:
            print(f"Skipping invalid event {row['id']}: {e}")

    db.commit()

def parse_time_remaining(text):
    text = text.lower().strip()
    if "hour" in text:
        return timedelta(hours=int(text.split()[0]))
    elif "min" in text:
        return timedelta(minutes=int(text.split()[0]))
    return timedelta(minutes=30)  # fallback default

# def get_all_events():
#     db = get_db()
#     return db.execute("""
#         SELECT e.*, u.name AS author_name 
#         FROM events e
#         JOIN user u ON e.author_email = u.email
#     """).fetchall()
def get_all_events():
    db = get_db()
    return db.execute("""
        SELECT e.*, u.name AS author_name, u.email AS author_email
        FROM events e
        LEFT JOIN user u ON e.author_email = u.email
        ORDER BY e.created_at DESC
    """).fetchall()


def insert_user(user):
    db = get_db()
    db.execute("""
        INSERT OR IGNORE INTO user (email, name, password)
        VALUES (?, ?, ?)
    """, (user["email"], user["name"], user["password"]))
    db.commit()
