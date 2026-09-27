from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    jsonify
)

from supabase import create_client, Client


# =========================================================
# SUPABASE CONFIGURATION
# =========================================================

SUPABASE_URL = "https://kubyedexweoutzsteaas.supabase.co"

# IMPORTANT:
# Paste your NEW Supabase key here.
# Do NOT share this key in chat or commit it to GitHub.
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt1YnllZGV4d2VvdXR6c3RlYWFzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc5MDUyMzcxNCwiZXhwIjoyMTA2MDk5NzE0fQ.9nuEdNrDCBiOnG2di2FkM4CnTdKIoh8kAKvLPTKB6H8"


# =========================================================
# SUPABASE CONNECTION
# =========================================================

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

app.secret_key = "careconnect-secret-key-change-in-production"


# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():
    return render_template("index.html")


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    try:

        patients_response = (
            supabase
            .table("patients")
            .select("id", count="exact")
            .execute()
        )

        appointments_response = (
            supabase
            .table("appointments")
            .select("id", count="exact")
            .execute()
        )

        pending_response = (
            supabase
            .table("appointments")
            .select("id", count="exact")
            .eq("status", "Pending")
            .execute()
        )

        ambulance_response = (
            supabase
            .table("ambulance_requests")
            .select("id", count="exact")
            .execute()
        )

        blood_response = (
            supabase
            .table("blood_requests")
            .select("id", count="exact")
            .eq("status", "Open")
            .execute()
        )

        patients = patients_response.count or 0
        appointments = appointments_response.count or 0
        pending_appointments = pending_response.count or 0
        ambulance_requests = ambulance_response.count or 0
        blood_requests = blood_response.count or 0

        return render_template(
            "dashboard.html",
            patients=patients,
            appointments=appointments,
            pending_appointments=pending_appointments,
            ambulance_requests=ambulance_requests,
            blood_requests=blood_requests
        )

    except Exception as e:

        return f"Dashboard database error: {e}", 500


# =========================================================
# PATIENTS
# =========================================================

@app.route("/patients")
def patients():

    try:

        search = request.args.get("search", "").strip()

        query = (
            supabase
            .table("patients")
            .select("*")
            .order("id", desc=True)
        )

        if search:

            query = query.or_(
                f"name.ilike.%{search}%,"
                f"phone.ilike.%{search}%,"
                f"blood_group.ilike.%{search}%,"
                f"location.ilike.%{search}%"
            )

        response = query.execute()

        patients_data = response.data or []

        return render_template(
            "patients.html",
            patients=patients_data,
            search=search
        )

    except Exception as e:

        return f"Patients database error: {e}", 500


@app.route("/patients/add", methods=["POST"])
def add_patient():

    try:

        name = request.form["name"]
        phone = request.form["phone"]

        age = request.form.get("age") or None
        gender = request.form.get("gender") or None
        blood_group = request.form.get("blood_group") or None
        location = request.form.get("location") or None

        supabase.table("patients").insert({

            "name": name,
            "phone": phone,
            "age": age,
            "gender": gender,
            "blood_group": blood_group,
            "location": location

        }).execute()

        return redirect(url_for("patients"))

    except Exception as e:

        return f"Add patient error: {e}", 500


# =========================================================
# APPOINTMENTS
# =========================================================

@app.route("/appointments")
def appointments():

    try:

        response = (
            supabase
            .table("appointments")
            .select("*, patients(name, phone)")
            .order("appointment_date")
            .order("appointment_time")
            .execute()
        )

        appointments_data = []

        for item in response.data or []:

            patient = item.get("patients") or {}

            item["patient_name"] = patient.get(
                "name",
                ""
            )

            item["patient_phone"] = patient.get(
                "phone",
                ""
            )

            appointments_data.append(item)

        patients_response = (
            supabase
            .table("patients")
            .select("*")
            .order("name")
            .execute()
        )

        patients_data = patients_response.data or []

        today = datetime.now().strftime("%Y-%m-%d")

        return render_template(
            "appointments.html",
            appointments=appointments_data,
            patients=patients_data,
            today=today
        )

    except Exception as e:

        return f"Appointments database error: {e}", 500


@app.route("/appointments/add", methods=["POST"])
def add_appointment():

    try:

        patient_id = request.form["patient_id"]
        doctor = request.form["doctor"]
        appointment_date = request.form["appointment_date"]
        appointment_time = request.form["appointment_time"]
        reason = request.form.get("reason") or None

        supabase.table("appointments").insert({

            "patient_id": patient_id,
            "doctor": doctor,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "reason": reason,
            "status": "Pending"

        }).execute()

        return redirect(url_for("appointments"))

    except Exception as e:

        return f"Add appointment error: {e}", 500


@app.route(
    "/appointments/status/<int:appointment_id>/<status>",
    methods=["GET", "POST"]
)
def update_appointment_status(
    appointment_id,
    status
):

    try:

        allowed_status = [
            "Pending",
            "Confirmed",
            "Completed",
            "Cancelled"
        ]

        if status not in allowed_status:
            return "Invalid appointment status", 400

        supabase.table("appointments").update({
            "status": status
        }).eq(
            "id",
            appointment_id
        ).execute()

        return redirect(url_for("appointments"))

    except Exception as e:

        return f"Appointment status error: {e}", 500


# =========================================================
# AMBULANCE
# =========================================================

@app.route("/ambulance")
def ambulance():

    try:

        response = (
            supabase
            .table("ambulance_requests")
            .select("*")
            .order("id", desc=True)
            .execute()
        )

        requests_data = response.data or []

        return render_template(
            "ambulance.html",
            requests=requests_data
        )

    except Exception as e:

        return f"Ambulance database error: {e}", 500


@app.route("/ambulance/add", methods=["POST"])
def add_ambulance():

    try:

        supabase.table("ambulance_requests").insert({

            "patient_name":
                request.form["patient_name"],

            "phone":
                request.form["phone"],

            "pickup_location":
                request.form["pickup_location"],

            "destination":
                request.form.get("destination") or None,

            "emergency_level":
                request.form.get("emergency_level") or None,

            "status":
                "Requested"

        }).execute()

        return redirect(url_for("ambulance"))

    except Exception as e:

        return f"Add ambulance request error: {e}", 500


@app.route(
    "/ambulance/status/<int:request_id>/<status>",
    methods=["GET", "POST"]
)
def update_ambulance_status(
    request_id,
    status
):

    try:

        allowed_status = [
            "Requested",
            "Assigned",
            "On the Way",
            "Completed",
            "Cancelled"
        ]

        if status not in allowed_status:
            return "Invalid ambulance status", 400

        supabase.table("ambulance_requests").update({

            "status": status

        }).eq(
            "id",
            request_id
        ).execute()

        return redirect(url_for("ambulance"))

    except Exception as e:

        return f"Ambulance status error: {e}", 500


# =========================================================
# BLOOD
# =========================================================

@app.route("/blood")
def blood():

    try:

        response = (
            supabase
            .table("blood_requests")
            .select("*")
            .order("id", desc=True)
            .execute()
        )

        requests_data = response.data or []

        facilities_response = (
            supabase
            .table("facilities")
            .select("*")
            .eq("type", "Blood Bank")
            .order("name")
            .execute()
        )

        facilities_data = (
            facilities_response.data or []
        )

        return render_template(
            "blood.html",
            requests=requests_data,
            facilities=facilities_data
        )

    except Exception as e:

        return f"Blood database error: {e}", 500


@app.route("/blood/add", methods=["POST"])
def add_blood_request():

    try:

        supabase.table("blood_requests").insert({

            "patient_name":
                request.form["patient_name"],

            "blood_group":
                request.form["blood_group"],

            "units":
                int(request.form["units"]),

            "location":
                request.form["location"],

            "contact":
                request.form["contact"],

            "status":
                "Open"

        }).execute()

        return redirect(url_for("blood"))

    except Exception as e:

        return f"Add blood request error: {e}", 500


# =========================================================
# FACILITIES
# =========================================================

@app.route("/facilities")
def facilities():

    try:

        response = (
            supabase
            .table("facilities")
            .select("*")
            .order("name")
            .execute()
        )

        facilities_data = response.data or []

        return render_template(
            "facilities.html",
            facilities=facilities_data
        )

    except Exception as e:

        return f"Facilities database error: {e}", 500


@app.route("/facilities/add", methods=["POST"])
def add_facility():

    try:

        supabase.table("facilities").insert({

            "name":
                request.form["name"],

            "type":
                request.form["type"],

            "location":
                request.form["location"],

            "phone":
                request.form.get("phone") or None,

            "emergency_available":
                request.form.get(
                    "emergency_available",
                    "Yes"
                )

        }).execute()

        return redirect(url_for("facilities"))

    except Exception as e:

        return f"Add facility error: {e}", 500


# =========================================================
# API - DASHBOARD STATISTICS
# =========================================================

@app.route("/api/stats")
def stats():

    try:

        patients = (
            supabase
            .table("patients")
            .select("id", count="exact")
            .execute()
        )

        appointments = (
            supabase
            .table("appointments")
            .select("id", count="exact")
            .execute()
        )

        ambulance = (
            supabase
            .table("ambulance_requests")
            .select("id", count="exact")
            .execute()
        )

        blood = (
            supabase
            .table("blood_requests")
            .select("id", count="exact")
            .execute()
        )

        return jsonify({

            "patients":
                patients.count or 0,

            "appointments":
                appointments.count or 0,

            "ambulance":
                ambulance.count or 0,

            "blood":
                blood.count or 0

        })

    except Exception as e:

        return jsonify({

            "status": "error",
            "error": str(e)

        }), 500


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health")
def health():

    try:

        supabase.table(
            "patients"
        ).select(
            "id"
        ).limit(
            1
        ).execute()

        return jsonify({

            "status":
                "healthy",

            "database":
                "supabase connected"

        }), 200

    except Exception as e:

        return jsonify({

            "status":
                "unhealthy",

            "database":
                "supabase connection failed",

            "error":
                str(e)

        }), 500


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )