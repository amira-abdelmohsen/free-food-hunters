DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS events;

CREATE TABLE user (
  email TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_email TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  location TEXT NOT NULL,
  pickup_time TEXT NOT NULL,
  pickup_end TEXT NOT NULL,
  allergies TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (author_email) REFERENCES user(email)
);
