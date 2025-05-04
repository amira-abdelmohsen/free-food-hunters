'''
Database interface and definition to store events and login information created by the app
'''
import sqlite3
import os
from datetime import datetime

import click
from flask import current_app, g

# Call this function when initializing the app to initialize the database and give it a propare set up
def init_app(app):
    # app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

# helper function for initialization
def init_db():
    db = get_db()
    with current_app.open_resource('events.sql') as f:
        db.executescript(f.read().decode('utf8'))

# def get_db():
#     if 'db' not in g:
#         g.db = sqlite3.connect(
#             current_app.config['DATABASE'],
#             detect_types=sqlite3.PARSE_DECLTYPES
#         )
#         g.db.row_factory = sqlite3.Row
#     return g.db

# use this function whenever accessing the database
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db




# def close_db(e=None):
#     db = g.pop('db', None)
#     if db is not None:
#         db.close()


# In the case database should be deleted, uncomment
# def close_db(e=None):
#     db = g.pop('db', None)
#     if db is not None:
#         db.close()

# cli database creation
@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

# Adds event onto database
def insert_event(data):
    db = get_db()
    db.execute("""
        INSERT INTO events (author_email, title, description, location, pickup_time, pickup_end, allergies)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data["author_email"],
        data["title"],
        data["description"],
        data["location"],
        data["pickup_time"],
        data["pickup_end"],
        data["allergies"]
    ))
    db.commit()

# Access events by a specific author
#   email - text form of the email that is used to look up in database
def get_events_by_author(email):
    db = get_db()
    return db.execute("SELECT * FROM events WHERE author_email = ?", (email,)).fetchall()

# Remove event by id from database
#   id - unique number to a created event in the database
def delete_event(event_id):
    db = get_db()
    db.execute("DELETE FROM events WHERE id = ?", (event_id,))
    db.commit()

# Automatic deletion of expired events. Event is expired if the given timeframe on creation is passed
def delete_expired_events():
    db = get_db()
    now = datetime.now()
    rows = db.execute("SELECT id, created_at, pickup_end FROM events").fetchall()

    for row in rows:
        try:
            created = row["created_at"] if isinstance(row["created_at"], datetime) else datetime.fromisoformat(str(row["created_at"]))
            end_time = datetime.strptime(row["pickup_end"], "%H:%M").time()
            expires_at = datetime.combine(created.date(), end_time)

            if expires_at <= now:
                db.execute("DELETE FROM events WHERE id = ?", (row["id"],))
        except Exception as e:
            print(f"Skipping invalid event {row['id']}: {e}")

    db.commit()

# Access all events in database. Used to show events on dashboard
def get_all_events():
    db = get_db()
    return db.execute("""
        SELECT e.*, u.name AS author_name, u.email AS author_email
        FROM events e
        LEFT JOIN user u ON e.author_email = u.email
        ORDER BY e.created_at DESC
    """).fetchall()

# Insert user into the database on registration
def insert_user(user):
    db = get_db()
    db.execute("""
        INSERT OR IGNORE INTO user (email, name, password)
        VALUES (?, ?, ?)
    """, (user["email"], user["name"], user["password"]))
    db.commit()
