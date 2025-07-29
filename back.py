from flask import Flask, render_template, request, redirect, jsonify, session, abort, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
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
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to /login if user is not authenticated

# User model for Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.email = user_data['email']
        self.name = user_data['name']
        self.role = user_data['role']
        self.department = user_data.get('department')

    @staticmethod
    def get(user_id):
        user_data = users_col.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return User(user_data)
        return None

@login_manager.user_loader
def load_user(user_id):
    """Flask-Login hook to load a user from the database."""
    return User.get(user_id)

@app.before_request
def logout_on_refresh():
    """
    Logs out the user on page refresh or subsequent navigation.
    This is achieved by clearing the session on any request to a protected
    page, unless a special 'just_logged_in' flag is present in the session.
    This flag is set only upon a successful login or passkey verification.
    """
    # Endpoints that are public and should not trigger the logout logic.
    public_endpoints = ['login', 'register', 'home', 'static', 'login_failed', 'logout']

    if request.endpoint in public_endpoints or not current_user.is_authenticated:
        return

    # If the one-time 'just_logged_in' flag is present, consume it and allow the request.
    if session.pop('just_logged_in', None):
        return

    # If the flag is not present, this is a subsequent request (e.g., refresh), so log the user out.
    logout_user()

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
    if current_user.is_authenticated:
        # If user is already logged in, redirect them appropriately
        return(redirect(url_for("logout")))

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"].lower()

        # Verify user credentials
        user_data = users_col.find_one({"email": email, "password": password, "role": role})
        if user_data:
            user_obj = User(user_data)
            login_user(user_obj)  # This handles the session management
            session['just_logged_in'] = True # Set one-time flag for logout-on-refresh

            if role == "citizen":
                print("citizen logged in, redirecting to /submit-complaint")
                # Redirect citizens to /submit-complaint
                return redirect(url_for("submit_complaint"))
            else:
                print(f"{role} logged in, redirecting to /official-dashboard")
                return redirect(url_for("passkey"))
        else:
            return render_template("login.html", error="Invalid login credentials.")

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    """Logs the user out and redirects to the homepage."""
    logout_user()
    return redirect(url_for("login"))

# Login Failed page
@app.route("/login_failed")   
def login_failed():
    return render_template("login_failed.html")

#to generate unique officer code
def generate_officer_code():
    return f"OFF-{random.randint(1000, 9999)}"


# Passkey page for Mayor and Municipal Officer login
@app.route("/passkey", methods=["GET", "POST"])
@login_required
def passkey():
    if current_user.role == 'citizen':
        return redirect(url_for('submit_complaint'))

    if request.method == "POST":
        entered_passkey = request.form.get("passkey")

        # Officer Passkey
        if entered_passkey == OFFICER_PASSKEY:
            if current_user.role == "official":
                if not officers_col.find_one({"email": current_user.email}):
                    officers_col.insert_one({
                        "officer_code": generate_officer_code(),
                        "name": current_user.name,
                        "email": current_user.email,
                        "department": current_user.department,
                        "is_available": True
                    })
                session['just_logged_in'] = True # Set one-time flag
                return redirect(url_for("official_dashboard"))
            else:
                # If user is not an official, show error
                return render_template("verification_failed.html")

        # Mayor Passkey
        elif entered_passkey == MAYOR_PASSKEY:
            if current_user.role == "mayor":
                session['just_logged_in'] = True # Set one-time flag
                return redirect(url_for("mayor_options"))
            else:
                return render_template("verification_failed.html")

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
@login_required
def submit_complaint():
    if request.method == "POST":
        title = request.form.get("title")
        category = request.form.get("category")
        description = request.form.get("description")

        user_id = current_user.id
        user_name = current_user.name
        user_email = current_user.email
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
@login_required
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
@login_required
def take_up_complaint(complaint_id):
    if current_user.role != "official":
        abort(403)  # Forbidden for non-officials

    officer_email = current_user.email
    officer_name = current_user.name
    officer_dept = current_user.department

    # Try to assign the complaint to THIS officer, but only if:
    # - it is still unassigned (or has an empty string)
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
@login_required
def mark_resolved(complaint_id):
    if current_user.role != "official":
        abort(403)  # Forbidden for non-officials

    officer_email = current_user.email
    officer_name = current_user.name
    officer_dept = current_user.department

    # Update complaint: mark as resolved and ensure officer info is stored
    result = complaints_col.update_one(
        {
            "_id": ObjectId(complaint_id),
            "assigned_officer": officer_name,  # BUGFIX: Check against name, which is what take_up sets
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
@login_required
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
@login_required
def mayor_options():
    if current_user.role != "mayor":
        abort(403) # Forbidden for non-mayors
    return render_template("mayor_options.html")


#Page showing only category of complaints Officer logged in by
@app.route("/official-dashboard")
@login_required
def official_dashboard():
    officer_email = current_user.email  # Officer’s email from session
    officer = officers_col.find_one({"email": officer_email})
    if not officer:
        return redirect("/login")

    # Filter complaints by officer's category
    officer_category = current_user.department  # Assuming department is the category
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
@login_required
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

if __name__ == "__main__":
    app.run(debug=True)