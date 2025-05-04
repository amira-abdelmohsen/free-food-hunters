import os
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import db
from db import insert_user


app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',  # Change this at deployment!
    DATABASE=os.path.join(app.instance_path, 'free-food-app.sqlite')
)



# Ensure instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

db.init_app(app)

# Custom Jinja filter to convert "14:00" to "02:00 PM"
@app.template_filter("datetimeformat")
def datetimeformat(value, format="%I:%M %p"):
    try:
        return datetime.strptime(value, "%H:%M").strftime(format)
    except Exception:
        return value  # fallback if parsing fails


@app.route("/")
def home():
    from db import delete_expired_events
    delete_expired_events()
    return render_template("index.html")  # Student food feed to be added later

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
            "time_remaining": request.form["time_remaining"],
            "allergies": ", ".join(request.form.getlist("allergies")),
            "author_email": session["email"]
        }
        from db import insert_event
        insert_event(new_event)
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

        if email == "admin@myhunter.cuny.edu" and password == "hunter123":
            session["email"] = email
            session["role"] = "student"
            return redirect(url_for("dashboard", role="student"))
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    role = request.args.get("role")
    if request.method == "POST":
        role = request.form["role"]
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        valid_domains = ["@hunter.cuny.edu", "@myhunter.cuny.edu"]
        if not any(email.endswith(domain) for domain in valid_domains):
            return render_template("register.html", selected_role=role, error="Please use your Hunter College email.")

        # Save user to DB
        insert_user({
            "email": email,
            "name": name,
            "password": password
        })

        # Log the user in and redirect
        session["email"] = email
        session["role"] = role
        return redirect(url_for("dashboard", role=role))

    return render_template("register.html", selected_role=role)

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


@app.route("/delete/<int:event_id>", methods=["POST"])
def delete_event_route(event_id):
    if "email" not in session:
        return redirect(url_for("login"))
    from db import delete_event
    delete_event(event_id)
    return redirect(url_for("dashboard", role="organizer"))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/debug-events")
def debug_events():
    from db import get_all_events
    events = get_all_events()
    return f"Found {len(events)} events:<br><br>" + "<br>".join([f"{e['title']} by {e['author_email']}" for e in events])


if __name__ == "__main__":
    app.run(debug=True)
