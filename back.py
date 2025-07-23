from flask import Flask, render_template, request, redirect, jsonify, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secretkey1234567890"  # Required for session management

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["active_city"]
users_col = db["users"]
complaints_col = db["complaints"]

# Homepage
@app.route("/")
def home():
    return render_template("home.html")

# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = users_col.find_one({"email": email, "password": password})
        if user:
            session["user_id"] = str(user["_id"])
            session["user_name"] = user["name"]
            session["user_email"] = email
            return redirect("/submit-complaint")
        else:
            return "Login failed"
    return render_template("login.html")

# Registration page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["fullname"]
        email = request.form["email"]
        password = request.form["password"]

        if users_col.find_one({"email": email}):
            return "User already exists or registration failed"
        users_col.insert_one({"name": name, "email": email, "password": password})
        return redirect("/login")
    return render_template("register.html")

# Complaint submission page
@app.route("/submit-complaint", methods=["GET", "POST"])
def submit_complaint():
    if request.method == "POST":
        title = request.form.get("title")
        category = request.form.get("category")
        description = request.form.get("description")

        user_id = session.get("user_id")
        if not user_id:
            return redirect("/login")  # user not logged in

        user = users_col.find_one({"_id": ObjectId(user_id)})
        if not user:
            return "User not found", 404

        user_name, user_email = user["name"], user["email"]
        submitted_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "Pending"

        complaints_col.insert_one({
            "user_id": user_id,
            "title": title,
            "category": category,
            "description": description,
            "submitted_on": submitted_on,
            "status": status
        })

        return render_template(
            "confirmation.html",
            name=user_name,
            email=user_email,
            category=category,
            description=description,
            submitted_on=submitted_on,
            status=status
        )

    return render_template("submit-complaint.html")  # for GET requests

@app.route("/admin")
def admin_dashboard():
    # Fetch pending complaints with user details
    pending = []
    for complaint in complaints_col.find({"status": "Pending"}):
        user = users_col.find_one({"_id": ObjectId(complaint["user_id"])})
        if user:
            pending.append([
                str(complaint["_id"]),
                user["name"],
                user["email"],
                complaint["description"]
            ])

    # Fetch resolved complaints with user details
    resolved = []
    for complaint in complaints_col.find({"status": "Resolved"}):
        user = users_col.find_one({"_id": ObjectId(complaint["user_id"])})
        if user:
            resolved.append([
                str(complaint["_id"]),
                user["name"],
                user["email"],
                complaint["description"]
            ])

    return render_template("admin_dashboard.html", pending=pending, resolved=resolved)

@app.route("/resolve/<complaint_id>", methods=["POST"])
def resolve_complaint(complaint_id):
    complaints_col.update_one(
        {"_id": ObjectId(complaint_id)},
        {"$set": {"status": "Resolved"}}
    )
    return redirect("/admin")  # Redirect back to admin dashboard

@app.route("/escalate", methods=["POST"])
def escalate():
    user_name = session.get("user_name")
    user_email = session.get("user_email")
    category = request.form.get("category")
    description = request.form.get("description")
    submitted_on = request.form.get("submitted_on")
    status = request.form.get("status")

    # Generate a custom escalation reference ID
    escalation_id = f"ESC{str(ObjectId())[:6].upper()}"

    return render_template(
        "escalated.html",
        name=user_name,
        email=user_email,
        category=category,
        description=description,
        submitted_on=submitted_on,
        escalation_id=escalation_id,
        status=status
    )

if __name__ == "__main__":
    app.run(debug=True)