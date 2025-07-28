from flask import Flask, jsonify, request, session
from flask_cors import CORS
from bson import ObjectId
from datetime import datetime

from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "secretkey1234567890" #required for session management
CORS(app)

client = MongoClient("mongodb://localhost:27017/")
db = client["active_city"]
users_col = db["users"]
complaints_col = db["complaints"]

@app.route("/submit-complaint", methods=["GET", "POST"])
def submit_complaint():
    data = request.get_json()
    title = data.get("title")
    category = data.get("category")
    description = data.get("description")

    user_id = session.get("user_id")
    print(f"User ID from session: {user_id}")
    if not user_id:
        return jsonify({"message": "User not logged in"}), 401

    user = users_col.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"message": "User not found"}), 404

    user_name, user_email = user["name"], user["email"]
    submitted_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "Pending"

    result = complaints_col.insert_one({
        "user_id": user_id,
        "title": title,
        "category": category,
        "description": description,
        "submitted_on": submitted_on,
        "status": status
    })
    complaint_id = str(result.inserted_id)

    return jsonify({
        "message": "Complaint submitted!",
        "name": user_name,
        "email": user_email,
        "category": category,
        "description": description,
        "submitted_on": submitted_on,
        "status": status,
        "_id": complaint_id
    }), 200

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = users_col.find_one({"email": email, "password": password})
    if user:
        session["user_id"] = str(user["_id"])
        session["user_name"] = user["name"]
        session["user_email"] = email
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Login failed, try making an account if you don't have one"}), 401
    
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("fullname")
    email = data.get("email")
    password = data.get("password")

    if users_col.find_one({"email": email}):
        return jsonify({"message": "User already exists or registration failed"}), 400

    users_col.insert_one({"name": name, "email": email, "password": password})
    return jsonify({"message": "Registration successful"}), 200



@app.route("/admin")
def admin_dashboard():
    # Fetch pending complaints with user details
    pending = []
    for complaint in complaints_col.find({"status": "Pending"}):
        user = users_col.find_one({"_id": ObjectId(complaint["user_id"])});
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
        user = users_col.find_one({"_id": ObjectId(complaint["user_id"])});
        if user:
            resolved.append([
                str(complaint["_id"]),
                user["name"],
                user["email"],
                complaint["description"]
            ])

    # Fetch escalated complaints
    escalated = []
    for escalation in db["escalations"].find():
        escalated.append([
            escalation.get("escalation_id", ""),
            escalation.get("user_name", ""),
            escalation.get("user_email", ""),
            escalation.get("category", ""),
            escalation.get("description", ""),
            escalation.get("submitted_on", ""),
            escalation.get("status", ""),
            escalation.get("complaint_id", "")
        ])

    return jsonify({"pending": pending, "resolved": resolved, "escalated": escalated})

@app.route("/escalate", methods=["POST"])
def escalate():
    # Accept JSON input from React frontend
    data = request.get_json()
    user_name = session.get("user_name")
    user_email = session.get("user_email")
    category = data.get("category")
    description = data.get("description")
    submitted_on = data.get("submitted_on")
    status = data.get("status")
    complaint_id = data.get("complaint_id")

    # Generate a custom escalation reference ID
    escalation_id = f"ESC{str(ObjectId())[:6].upper()}"

    # Save escalation to the database
    escalation_doc = {
        "user_name": user_name,
        "user_email": user_email,
        "category": category,
        "description": description,
        "submitted_on": submitted_on,
        "status": status,
        "escalation_id": escalation_id,
        "complaint_id": complaint_id
    }
    db["escalations"].insert_one(escalation_doc)

    return jsonify({
        "name": user_name,
        "email": user_email,
        "category": category,
        "description": description,
        "submitted_on": submitted_on,
        "escalation_id": escalation_id,
        "status": status
    }), 200

@app.route("/resolve/<complaint_id>", methods=["POST"])
def resolve_complaint(complaint_id):
    from bson.errors import InvalidId
    updated_complaint = False
    updated_escalation = False
    from bson.errors import InvalidId
    # Try to resolve complaint by ObjectId
    if len(complaint_id) == 24:
        try:
            result = complaints_col.update_one(
                {"_id": ObjectId(complaint_id)},
                {"$set": {"status": "Resolved"}}
            )
            if result.modified_count > 0:
                updated_complaint = True
        except InvalidId:
            pass
        # Also resolve any escalations linked to this complaint
        result2 = db["escalations"].update_many(
            {"complaint_id": complaint_id},
            {"$set": {"status": "Resolved"}}
        )
        updated_escalation = result2.modified_count > 0
    else:
        # If not a valid ObjectId, treat as escalation_id and resolve escalation
        result2 = db["escalations"].update_one(
            {"escalation_id": complaint_id},
            {"$set": {"status": "Resolved"}}
        )
        updated_escalation = result2.modified_count > 0
        # Find the escalation document to get the original complaint_id
        escalation_doc = db["escalations"].find_one({"escalation_id": complaint_id})
        if escalation_doc:
            orig_id = escalation_doc.get("complaint_id")
            if orig_id and len(orig_id) == 24:
                try:
                    result = complaints_col.update_one(
                        {"_id": ObjectId(orig_id)},
                        {"$set": {"status": "Resolved"}}
                    )
                    if result.modified_count > 0:
                        updated_complaint = True
                except InvalidId:
                    pass
    if updated_complaint and updated_escalation:
        msg = "Complaint and escalation marked as resolved."
    elif updated_complaint:
        msg = "Complaint marked as resolved."
    elif updated_escalation:
        msg = "Escalation marked as resolved."
    else:
        msg = "No matching complaint or escalation found."
    return jsonify({"message": msg}), 200

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"}), 200

if __name__ == '__main__':
    app.run(debug=True)