import os
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY = 'dev', # !!!OVER WRITE THIS TO A RANDOM KEY AT DEPLOYMENT!!!
    DATABASE = os.path.join(app.instance_path, 'free-food-app.sqlite')
)

food_data = [{
        "title": "Leftover Pizza",
        "description": "2 boxes left from CS Club",
        "location": "Room 101, Science Building",
        "time_remaining": "15 mins",
        "lat": 40.7128,
        "lng": -74.0060
    },
    {
        "title": "Free Sandwiches",
        "description": "Plenty available after meeting!",
        "location": "Student Union Lobby",
        "time_remaining": "30 mins",
        "lat": 40.7132,
        "lng": -74.0070
    }]  # Store food posts temporarily

try:
    os.makedirs(app.instance_path)
except OSError:
    pass


import db
db.init_app(app)

@app.route("/")
def home():
    return render_template("index.html", food_events=food_data, food_events_json=food_data)

@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        new_event = {
            "title": request.form["title"],
            "description": request.form["description"],
            "location": request.form["location"],
            "lat": float(request.form["lat"]),
            "lng": float(request.form["lng"]),
            "time_remaining": request.form["time_remaining"]
        }
        food_data.append(new_event)
        return redirect(url_for("home"))
    return render_template("submit.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Enforce Hunter email domains
        valid_domains = ["@hunter.cuny.edu", "@myhunter.cuny.edu"]
        if not any(email.endswith(domain) for domain in valid_domains):
            return render_template("login.html", error="Please use your Hunter College email.")

        # TODO: Dummy authentication logic (replace with real user from DB check later)
        if email == "admin@myhunter.cuny.edu" and password == "hunter123":
            session["email"] = email
            session["role"] = "student"  # default to student, can be changed
            return redirect(url_for("dashboard", role="student"))
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    role = request.args.get("role")  # from URL query param like ?role=organizer
    if request.method == "POST":
        role = request.form["role"]
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # Email domain enforcement
        valid_domains = ["@hunter.cuny.edu", "@myhunter.cuny.edu"]
        if not any(email.endswith(domain) for domain in valid_domains):
            return render_template("register.html", selected_role=role, error="Please use your Hunter College email.")

        # TODO: Save to DB here

        # Log the user in and redirect to their dashboard
        session["email"] = email
        session["role"] = role
        return redirect(url_for("dashboard", role=role))
    
    return render_template("register.html", selected_role=role)

@app.route("/dashboard")
def dashboard():
    if "email" not in session:
        return redirect(url_for("login"))

    role = request.args.get("role", session.get("role", "student"))  # fallback to session role
    user = session.get("email", "Guest")

    if role == "organizer":
        return render_template("dashboard-organizer.html", user=user)
    else:
        return render_template("dashboard-student.html", user=user)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))




if __name__ == "__main__":
    app.run(debug=True)