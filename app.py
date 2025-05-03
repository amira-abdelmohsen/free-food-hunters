from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

food_data = []  # Store food posts temporarily

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

if __name__ == "__main__":
    app.run(debug=True)
