'''Free Food Finder application'''

import os
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import db
from db import insert_user
import ssl
import certifi
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
from twilio.rest import Client
load_dotenv()

# App initialization and configuration
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'free-food-app.sqlite')
)

# Ensure database exists on first run
os.makedirs(app.instance_path, exist_ok=True)
db_path = app.config["DATABASE"]
if not os.path.exists(db_path):
    with app.app_context():
        db.init_db()


@app.template_filter("datetimeformat")
def datetimeformat(value, format="%I:%M %p"):
    try:
        return datetime.strptime(value, "%H:%M").strftime(format)
    except Exception:
        return value

# Home/Start page definition
@app.route("/")
def home():
    from db import delete_expired_events
    delete_expired_events()
    return render_template("index.html")

# Event submission definition
@app.route("/submit", methods=["GET", "POST"])
def submit():
    if "email" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        new_event = {
            "title": request.form["title"],
            "description": request.form["description"],
            "location": request.form["location"],
            "pickup_time": request.form["pickup_time"],
            "pickup_end": request.form["pickup_end"],
            "allergies": ", ".join(request.form.getlist("allergies")),
            "author_email": session["email"]
        }

        from db import insert_event
        insert_event(new_event)

        # ✅ Now the email goes AFTER the event is defined
        from mail_utils import send_email
        send_email(
            to_email="student@myhunter.cuny.edu",  # Replace with real student emails later
            subject="🍕 New Free Food Alert!",
            content=f"{new_event['title']} is available at {new_event['location']}.\n\nDetails: {new_event['description']}"
        )

        return redirect(url_for("dashboard", role="organizer"))

    return render_template("submit.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        valid_domains = ["@hunter.cuny.edu", "@myhunter.cuny.edu"]
        if not any(email.endswith(domain) for domain in valid_domains):
            return render_template("login.html", error="Please use your Hunter College email.")
        if "email" in session:
            return redirect(url_for("dashboard", role=session.get("role")))

        db_conn = db.get_db()
        user = db_conn.execute(
            "SELECT * FROM user WHERE email = ? AND password = ?", (email, password)
        ).fetchone()

        if user:
            session["email"] = user["email"]
            session["role"] = request.form.get("role", "student")  # fallback
            return redirect(url_for("dashboard", role=session["role"]))
        else:
            return render_template("login.html", error="Invalid email or password.")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if "email" in session:
        return redirect(url_for("dashboard", role=session.get("role")))
    role = request.args.get("role")
    if request.method == "POST":
        role = request.form["role"]
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        error = None

        valid_domains = ["@hunter.cuny.edu", "@myhunter.cuny.edu"]
        if not any(email.endswith(domain) for domain in valid_domains):
            error = "Please use your Hunter College email."
        elif not name:
            error = "Name is required."
        elif not password:
            error = "Password is required."

        if error is None:
            try:
                from db import insert_user
                insert_user({
                    "email": email,
                    "name": name,
                    "password": password
                })
                session["email"] = email
                session["role"] = role
                return redirect(url_for("dashboard", role=role))
            except Exception as e:
                error = f"Registration failed: {e}"

        return render_template("register.html", selected_role=role, error=error)

    return render_template("register.html", selected_role=role)

# Dashboard definition
@app.route("/dashboard")
def dashboard():
    if "email" not in session:
        return redirect(url_for("login"))

    from db import delete_expired_events, get_events_by_author
    delete_expired_events()

    role = request.args.get("role", session.get("role", "student"))
    user = session["email"]

    if role == "organizer":
        events = get_events_by_author(user)
        return render_template("dashboard-organizer.html", user=user, events=events)
    else:
        from db import get_all_events
        events = get_all_events()
        return render_template("dashboard-student.html", user=user, events=events)

# Delete event button definition
@app.route("/delete/<int:event_id>", methods=["POST"])
def delete_event_route(event_id):
    if "email" not in session:
        return redirect(url_for("login"))
    from db import delete_event
    delete_event(event_id)
    return redirect(url_for("dashboard", role="organizer"))

# About page definition
@app.route("/about")
def about():
    return render_template("about.html")

# Logout function definition
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

#
@app.route("/debug-events")
def debug_events():
    from db import get_all_events
    events = get_all_events()
    return f"Found {len(events)} events:<br><br>" + "<br>".join([f"{e['title']} — {e['pickup_time']} to {e['pickup_end']}" for e in events])



# Push email notification subscription definition
@app.route("/subscribe", methods=["POST"])
def subscribe():
    if "email" not in session:
        return redirect(url_for("login"))

    user_email = session["email"]

    try:
        client = Client(
            os.environ["TWILIO_ACCOUNT_SID"],
            os.environ["TWILIO_AUTH_TOKEN"]
        )

        verification = client.verify.v2.services(
            os.environ["TWILIO_VERIFY_SERVICE_SID"]
        ).verifications.create(
            channel="email",
            to=user_email
        )

        print("Verification SID:", verification.sid)
        print("Verification Status:", verification.status)
        return redirect(url_for("dashboard", role="student", subscribed="true"))

    except Exception as e:
        print("Twilio error:", str(e))
        return redirect(url_for("dashboard", role="student", error="true"))

# Program start
if __name__ == "__main__":
    app.run(debug=True)
