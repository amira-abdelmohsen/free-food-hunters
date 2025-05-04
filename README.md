# free-food-hunters
# 🍕 Free Food Finder

A web application that helps reduce food waste by notifying students about leftover food from campus events.

## 🚀 Features

- 🔐 Authentication for Students and Organizers (Hunter College emails only)
- 📍 Google Maps integration for visualizing food event locations
- 📝 Organizers can post available food with location, time, and allergy info
- 🔔 Students receive real-time alerts about food availability (via browser or email)
- 🧠 Smart routing — users are redirected to dashboard if already logged in
- 🧼 Automatic cleanup of expired events

## 🛠️ Tech Stack

- **Backend**: Python, Flask, SQLite
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Email Notifications**: SendGrid API
- **Session Handling**: Flask Sessions
- **Environment Management**: python-dotenv

## 📦 Setup Instructions

1. **Clone the repository:**

   ```bash
   git clone https://github.com/amira-abdelmohsen/free-food-hunters.git
   cd free-food-hunters
2. **Set up environments**
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

3.**install dependencies**
pip install -r requirements.txt

4. **Set up .env file**
SENDGRID_API_KEY=your_sendgrid_key_here


5. **Run the app:**
flask --app app.py run


Visit http://localhost:5000


