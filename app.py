import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from database import get_db, init_db
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "careconnect-secret-key-change-in-production")

# Initialize database
init_db()


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@app.route("/dashboard")
def dashboard():

    conn = get_db()

    patients = conn.execute(
        "SELECT COUNT(*) AS total FROM patients"
    ).fetchone()["total"]

    appointments = conn.execute(
        "SELECT COUNT(*) AS total FROM appointments"
    ).fetchone()["total"]

    pending_appointments = conn.execute(
        "SELECT COUNT(*) AS total FROM appointments WHERE status='Pending'"
    ).fetchone()["total"]

    ambulance_requests = conn.execute(
        "SELECT COUNT(*) AS total FROM ambulance_requests"
    ).fetchone()["total"]

    blood_requests = conn.execute(
        "SELECT COUNT(*) AS total FROM blood_requests WHERE status='Open'"
    ).fetchone()["total"]

    conn.close()

    return render_template(
        "dashboard.html",
        patients=patients,
        appointments=appointments,
        pending_appointments=pending_appointments,
        ambulance_requests=ambulance_requests,
        blood_requests=blood_requests
    )


# --------------------------------------------------
# PATIENTS
# --------------------------------------------------

@app.route("/patients")
def patients():

    conn = get_db()

    search = request.args.get("search", "")

    if search:

        patients = conn.execute("""
            SELECT *
            FROM patients
            WHERE name LIKE ?
            OR phone LIKE ?
            OR blood_group LIKE ?
            OR location LIKE ?
            ORDER BY id DESC
        """, (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        )).fetchall()

    else:

        patients = conn.execute("""
            SELECT *
            FROM patients
            ORDER BY id DESC
        """).fetchall()

    conn.close()

    return render_template(
        "patients.html",
        patients=patients,
        search=search
    )


@app.route("/patients/add", methods=["POST"])
def add_patient():

    name = request.form["name"]
    phone = request.form["phone"]
    age = request.form["age"]
    gender = request.form["gender"]
    blood_group = request.form["blood_group"]
    location = request.form["location"]

    conn = get_db()

    conn.execute("""
        INSERT INTO patients
        (name, phone, age, gender, blood_group, location)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        name,
        phone,
        age,
        gender,
        blood_group,
        location
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("patients"))


# --------------------------------------------------
# APPOINTMENTS
# --------------------------------------------------

@app.route("/appointments")
def appointments():

    conn = get_db()

    appointments = conn.execute("""
        SELECT
            appointments.*,
            patients.name AS patient_name,
            patients.phone AS patient_phone
        FROM appointments
        JOIN patients
        ON appointments.patient_id = patients.id
        ORDER BY appointment_date, appointment_time
    """).fetchall()

    patients = conn.execute("""
        SELECT *
        FROM patients
        ORDER BY name
    """).fetchall()

    conn.close()

    today = datetime.now().strftime("%Y-%m-%d")

    return render_template(
        "appointments.html",
        appointments=appointments,
        patients=patients,
        today=today
    )


@app.route("/appointments/add", methods=["POST"])
def add_appointment():

    patient_id = request.form["patient_id"]
    doctor = request.form["doctor"]
    appointment_date = request.form["appointment_date"]
    appointment_time = request.form["appointment_time"]
    reason = request.form["reason"]

    conn = get_db()

    conn.execute("""
        INSERT INTO appointments
        (
            patient_id,
            doctor,
            appointment_date,
            appointment_time,
            reason
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        patient_id,
        doctor,
        appointment_date,
        appointment_time,
        reason
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("appointments"))


@app.route("/appointments/status/<int:appointment_id>/<status>", methods=["GET", "POST"])
@app.route("/appointments/status/<int:appointment_id>/<status>", methods=["GET", "POST"], endpoint="appointment_status")
def update_appointment_status(appointment_id, status):

    allowed_status = [
        "Pending",
        "Confirmed",
        "Completed",
        "Cancelled"
    ]

    if status not in allowed_status:
        return "Invalid status", 400

    conn = get_db()

    conn.execute("""
        UPDATE appointments
        SET status = ?
        WHERE id = ?
    """, (
        status,
        appointment_id
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("appointments"))


# --------------------------------------------------
# AMBULANCE
# --------------------------------------------------

@app.route("/ambulance")
def ambulance():

    conn = get_db()

    requests_data = conn.execute("""
        SELECT *
        FROM ambulance_requests
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "ambulance.html",
        requests=requests_data
    )


@app.route("/ambulance/add", methods=["POST"])
def add_ambulance():

    patient_name = request.form["patient_name"]
    phone = request.form["phone"]
    pickup_location = request.form["pickup_location"]
    destination = request.form["destination"]
    emergency_level = request.form["emergency_level"]

    conn = get_db()

    conn.execute("""
        INSERT INTO ambulance_requests
        (
            patient_name,
            phone,
            pickup_location,
            destination,
            emergency_level
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        patient_name,
        phone,
        pickup_location,
        destination,
        emergency_level
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("ambulance"))


@app.route("/ambulance/status/<int:request_id>/<status>", methods=["GET", "POST"])
def update_ambulance_status(request_id, status):

    allowed = [
        "Requested",
        "Assigned",
        "On the Way",
        "Completed",
        "Cancelled"
    ]

    if status not in allowed:
        return "Invalid status", 400

    conn = get_db()

    conn.execute("""
        UPDATE ambulance_requests
        SET status = ?
        WHERE id = ?
    """, (
        status,
        request_id
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("ambulance"))


# --------------------------------------------------
# BLOOD
# --------------------------------------------------

@app.route("/blood")
def blood():

    conn = get_db()

    requests_data = conn.execute("""
        SELECT *
        FROM blood_requests
        ORDER BY id DESC
    """).fetchall()

    facilities = conn.execute("""
        SELECT *
        FROM facilities
        WHERE type = 'Blood Bank'
        ORDER BY name
    """).fetchall()

    conn.close()

    return render_template(
        "blood.html",
        requests=requests_data,
        facilities=facilities
    )


@app.route("/blood/add", methods=["POST"])
def add_blood_request():

    patient_name = request.form["patient_name"]
    blood_group = request.form["blood_group"]
    units = request.form["units"]
    location = request.form["location"]
    contact = request.form["contact"]

    conn = get_db()

    conn.execute("""
        INSERT INTO blood_requests
        (
            patient_name,
            blood_group,
            units,
            location,
            contact
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        patient_name,
        blood_group,
        units,
        location,
        contact
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("blood"))


# --------------------------------------------------
# FACILITIES
# --------------------------------------------------

@app.route("/facilities")
def facilities():

    conn = get_db()

    facilities_data = conn.execute("""
        SELECT *
        FROM facilities
        ORDER BY name
    """).fetchall()

    conn.close()

    return render_template(
        "facilities.html",
        facilities=facilities_data
    )


@app.route("/facilities/add", methods=["POST"])
def add_facility():

    name = request.form["name"]
    facility_type = request.form["type"]
    location = request.form["location"]
    phone = request.form["phone"]
    emergency_available = request.form["emergency_available"]

    conn = get_db()

    conn.execute("""
        INSERT INTO facilities
        (
            name,
            type,
            location,
            phone,
            emergency_available
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        facility_type,
        location,
        phone,
        emergency_available
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("facilities"))


# --------------------------------------------------
# API - DASHBOARD STATISTICS
# --------------------------------------------------

@app.route("/api/stats")
def stats():

    conn = get_db()

    data = {
        "patients": conn.execute(
            "SELECT COUNT(*) AS total FROM patients"
        ).fetchone()["total"],

        "appointments": conn.execute(
            "SELECT COUNT(*) AS total FROM appointments"
        ).fetchone()["total"],

        "ambulance": conn.execute(
            "SELECT COUNT(*) AS total FROM ambulance_requests"
        ).fetchone()["total"],

        "blood": conn.execute(
            "SELECT COUNT(*) AS total FROM blood_requests"
        ).fetchone()["total"]
    }

    conn.close()

    return jsonify(data)


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.route("/health")
def health():
    try:
        conn = get_db()
        conn.execute("SELECT 1").fetchone()
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


# --------------------------------------------------
# RUN
# --------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1")
    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug
    )