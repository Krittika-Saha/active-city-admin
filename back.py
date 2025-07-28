from flask import Flask, render_template, request, redirect, jsonify, session, abort, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = "secretkey1234567890"  # Required for session management

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["active_city"]
users_col = db["users"]
complaints_col = db["complaints"]
officers_col = db["officers"]

#constant passkeys for mayor and municipal officer login or registration
OFFICER_PASSKEY = "officer123"
MAYOR_PASSKEY = "mayor123"

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
        role = request.form["role"].lower()

        # Verify user credentials
        user = users_col.find_one({"email": email, "password": password, "role": role})
        if user:
            session["user_id"] = str(user["_id"])
            session["user_name"] = user["name"]
            session["user_email"] = email
            session["user_role"] = role

            # For officials, fetch department from DB
            if role == "official":
                session["department"] = user.get("department", "Unassigned")
            else:
                session.pop("department", None)

            if role == "citizen":
                print("citizen logged in, redirecting to /submit-complaint")
                # Redirect citizens to /submit-complaint
                return redirect("/submit-complaint") 
            else:
                print(f"{role} logged in, redirecting to /official-dashboard")
                return redirect("/passkey")
        else:
            return render_template("login.html", error="Invalid login credentials.")

    return render_template("login.html")

# Login Failed page
@app.route("/login_failed")   
def login_failed():
    return render_template("login_failed.html")

#to generate unique officer code
def generate_officer_code():
    return f"OFF-{random.randint(1000, 9999)}"


# Passkey page for Mayor and Municipal Officer login
@app.route("/passkey", methods=["GET", "POST"])
def passkey():
    if request.method == "POST":
        entered_passkey = request.form.get("passkey")

        # Officer Passkey
        if entered_passkey == OFFICER_PASSKEY:
            user_id = session.get("user_id")
            user = users_col.find_one({"_id": ObjectId(user_id)})
            department = session.get("department", "Unassigned")  # Use department from session

            # Ensure only officials are added as officers
            if user and user.get("role") == "official":
                if not officers_col.find_one({"email": user["email"]}):
                    officers_col.insert_one({
                        "officer_code": generate_officer_code(),
                        "name": user["name"],
                        "email": user["email"],
                        "department": department,
                        "is_available": True
                    })
                return redirect("/official-dashboard")
            else:
                # If user is not an official, show error
                return render_template("verification_failed.html")

        # Mayor Passkey
        elif entered_passkey == MAYOR_PASSKEY:
            return redirect("/mayor-options")

        # Invalid Passkey
        else:
            return render_template("verification_failed.html")

    return render_template("passkey.html")

# Registration page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["fullname"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"].lower()
        department = request.form.get("department") if role == "official" else None

        # Check if user already exists before inserting
        if users_col.find_one({"email": email}):
            return "User already exists or registration failed"

        # Insert new user
        users_col.insert_one({
            "name": name,
            "email": email,
            "password": password,
            "role": role,
            "department": department
        })

        return redirect("/login")
    return render_template("register.html")

# ---------------- Submit Complaint ----------------
@app.route("/submit-complaint", methods=["GET", "POST"])
def submit_complaint():
    if request.method == "POST":
        title = request.form.get("title")
        category = request.form.get("category")
        description = request.form.get("description")
        # location = request.form.get("location")

        # Ensure user is logged in
        user_id = session.get("user_id")
        if not user_id:
            return redirect(url_for("login"))  # user not logged in

        user = users_col.find_one({"_id": ObjectId(user_id)})
        if not user:
            return "User not found", 404

        user_name, user_email = user["name"], user["email"]
        submitted_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "Pending"

        # Insert complaint (including name/email for easy reference)
        result = complaints_col.insert_one({
            "user_id": user_id,
            "name": user_name,  # ADD name
            "email": user_email,  # ADD email
            "title": title,
            "category": category,
            "description": description,
            "submitted_on": submitted_on,
            "status": status,
            # "location": location,
            "escalated_on": None,
            "assigned_officer": None
        })

        complaint_id = str(result.inserted_id)
        print("DEBUG: Complaint ID =", complaint_id)  # Debugging log

        # Pass complaint_id to confirmation page
        return render_template(
            "confirmation.html",
            complaint_id=complaint_id,
            name=user_name,
            email=user_email,
            category=category,
            description=description,
            submitted_on=submitted_on,
            escalated_on=None,  # No escalation date yet
            # location=location,  # ADD location
            status=status
        )

    return render_template("submit-complaint.html")

# ---------------- Escalate Complaint ----------------
@app.route("/escalate", methods=["POST"])
def escalate():
    complaint_id = request.form.get("complaint_id")
    print("DEBUG: Escalate received complaint_id =", complaint_id)  # Debugging log

    if not complaint_id:
        return "Error: Complaint ID missing.", 400

    # Update the complaint status to Escalated
    result = complaints_col.update_one(
        {"_id": ObjectId(complaint_id)},
        {"$set": {"status": "Escalated", "escalated_on": datetime.now()}}
    )

    if result.modified_count == 0:
        return "No complaint found or already escalated.", 404

    # Fetch updated complaint data
    complaint = complaints_col.find_one({"_id": ObjectId(complaint_id)})

    escalation_id = f"ESC{str(ObjectId())[:6].upper()}"

    return render_template(
        "escalated.html",
        escalation_id=escalation_id,
        name=complaint["name"],
        email=complaint["email"],
        category=complaint["category"],
        description=complaint["description"],
        submitted_on=complaint.get("submitted_on", "Unknown"),
        status="Escalated"
    )

@app.route("/take-up/<complaint_id>", methods=["POST"])
def take_up_complaint(complaint_id):
    # Only officials can take up complaints
    if session.get("user_role") != "official":
        return redirect("/login")

    officer_email = session.get("user_email")
    officer_name = session.get("user_name")  # Get officer name from session
    officer_dept = session.get("department")

    if not officer_email or not officer_dept:
        return redirect("/login")

    # Try to assign the complaint to THIS officer, but only if:
    # - it is still unassigned
    # - it belongs to the officer's department
    result = complaints_col.update_one(
        {
            "_id": ObjectId(complaint_id),
            "assigned_officer": {"$in": [None, ""]},
            "category": officer_dept,
            "status": "Pending"
        },
        {
            "$set": {"assigned_officer": officer_name}  # Store officer name
        }
    )

    # If we actually matched & modified a complaint, mark officer unavailable
    if result.modified_count == 1:
        officers_col.update_one(
            {"email": officer_email},
            {"$set": {"is_available": False}}
        )

    return redirect("/official-dashboard")

@app.route("/mark-resolved/<complaint_id>", methods=["POST"])
def mark_resolved(complaint_id):
    # Only officials can resolve complaints
    if session.get("user_role") != "official":
        return redirect("/login")

    officer_email = session.get("user_email")
    officer_name = session.get("user_name")
    officer_dept = session.get("department")

    if not officer_email or not officer_dept:
        return redirect("/login")

    # Update complaint: mark as resolved and ensure officer info is stored
    result = complaints_col.update_one(
        {
            "_id": ObjectId(complaint_id),
            "assigned_officer": officer_email,  # Only if this officer took it up
            "category": officer_dept
        },
        {
            "$set": {
                "status": "Resolved",
                "assigned_officer": officer_name  # Save officer name
            }
        }
    )

    # If resolved, mark officer as available
    if result.modified_count == 1:
        officers_col.update_one(
            {"email": officer_email},
            {"$set": {"is_available": True}}
        )

    return redirect("/official-dashboard")

# Officers page for the Users and Mayors  to veiw
@app.route("/officers")
def officers():
    # Fetch all officers
    all_officers = list(officers_col.find())

    # Group officers by department
    officers_by_dept = {}
    for officer in all_officers:
        dept = officer.get("department", "Other")
        if dept not in officers_by_dept:
            officers_by_dept[dept] = []
        officers_by_dept[dept].append(officer)

    return render_template("officers.html", officers_by_dept=officers_by_dept)

# Page for the Mayor after verification
@app.route("/mayor-options")
def mayor_options():
    if session.get("user_role") != "mayor":
        return redirect("/login")
    return render_template("mayor_options.html")


#Page showing only category of complaints Officer logged in by
@app.route("/official-dashboard")
def official_dashboard():
    officer_email = session.get("user_email")  # Officer’s email from session
    officer = officers_col.find_one({"email": officer_email})
    if not officer:
        return redirect("/login")

    # Filter complaints by officer's category
    officer_category = session.get("department")
    pending_complaints = complaints_col.find({"category": officer_category, "status": "Pending"})
    resolved_complaints = complaints_col.find({"category": officer_category, "status": "Resolved"})

    return render_template(
        "official_dashboard.html",
        pending_complaints=pending_complaints,
        resolved_complaints=resolved_complaints,
        officer_category=officer_category
    )

# Admin Dashboard for the Mayor
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

    # Fetch escalated complaints with user details
    escalated = []
    for complaint in complaints_col.find({"status": "Escalated"}):
        user = users_col.find_one({"_id": ObjectId(complaint["user_id"])})
        if user:
            escalated.append([
                str(complaint["_id"]),
                user["name"],
                user["email"],
                complaint["description"]
            ])

    # Fetch resolved complaints with user details and officer info
    resolved = []
    for complaint in complaints_col.find({"status": "Resolved"}):
        user = users_col.find_one({"_id": ObjectId(complaint["user_id"])})
        if user:
            resolved.append([
                str(complaint["_id"]),
                user["name"],
                user["email"],
                complaint["description"],
                complaint.get("assigned_officer", "Unknown Officer")  # Officer details
            ])

    return render_template(
        "admin_dashboard.html",
        pending=pending,
        escalated=escalated,
        resolved=resolved
    )

@app.route("/resolve/<complaint_id>", methods=["POST"])
def resolve_complaint(complaint_id):
    officer_email = session.get("user_email")
    officer = officers_col.find_one({"email": officer_email})
    officer_name = officer["name"] if officer else "Unknown Officer"

    complaints_col.update_one(
        {"_id": ObjectId(complaint_id)},
        {"$set": {"status": "Resolved", "assigned_officer": officer_name}}
    )

    # Optionally mark officer as available again
    if officer:
        officers_col.update_one({"email": officer_email}, {"$set": {"is_available": True}})

    return redirect("/admin")

# @app.route("/escalate", methods=["POST"])
# def escalate():
#     user_name = session.get("user_name")
#     user_email = session.get("user_email")
#     category = request.form.get("category")
#     description = request.form.get("description")
#     submitted_on = request.form.get("submitted_on")
#     status = request.form.get("status")

#     # Generate a custom escalation reference ID
#     escalation_id = f"ESC{str(ObjectId())[:6].upper()}"

#     return render_template(
#         "escalated.html",
#         name=user_name,
#         email=user_email,
#         category=category,
#         description=description,
#         submitted_on=submitted_on,
#         escalation_id=escalation_id,
#         status=status
#     )

if __name__ == "__main__":
    app.run(debug=True)