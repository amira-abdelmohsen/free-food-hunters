import os
from flask import Flask, render_template, request, redirect, url_for

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

        # Replace with real user check if needed
        if email == "admin@example.com" and password == "hunter123":
            return redirect(url_for("submit"))  # 👈 redirect to submission form after login
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

        # Simulate saving or pass to your DB logic
        print(f"{role} registered: {name} ({email})")

        return redirect(url_for("login"))

    return render_template("register.html", selected_role=role)


if __name__ == "__main__":
    app.run(debug=True)