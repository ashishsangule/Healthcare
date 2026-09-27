# CareConnect - Healthcare Coordination Platform

CareConnect is a modern Flask-based healthcare coordination web platform for managing patients, clinic appointments, emergency ambulance requests, and blood bank availability.

---

## Features
- **Clinic Dashboard**: Visual statistics and quick action links.
- **Patient Management**: Record patient info, contact, age, and blood group.
- **Appointment Scheduling**: Book appointments and update status (Pending, Confirmed, Completed, Cancelled).
- **Ambulance Coordination**: Manage emergency transport requests by urgency level.
- **Blood Coordination**: Track blood requests and view registered blood banks.
- **Healthcare Facilities**: Directory of hospitals, clinics, and blood banks.

---

## Deployment on Render

This project is configured and fully ready for deployment on [Render](https://render.com).

### Option 1: Native Python Web Service (Recommended)
1. In Render Dashboard, click **New +** -> **Web Service**.
2. Connect your Git repository.
3. Configure the settings:
   - **Environment / Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
4. Click **Deploy Web Service**.

> Render automatically sets the `PORT` environment variable (defaults to 10000). The included `gunicorn.conf.py` binds Gunicorn to `0.0.0.0:$PORT`.

---

### Option 2: Docker Web Service
1. In Render Dashboard, click **New +** -> **Web Service**.
2. Connect your Git repository.
3. Set **Runtime** to **Docker**.
4. Render will automatically detect `Dockerfile` and `.dockerignore`.
5. Click **Deploy Web Service**.

---

### Option 3: Render Blueprint (render.yaml)
1. In Render Dashboard, click **New +** -> **Blueprint**.
2. Connect your Git repository. Render will automatically read `render.yaml` and configure the service.

---

## Local Development

```bash
# Clone the repository
git clone <repo-url>
cd healthcare

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
```
Open `http://localhost:5000` in your browser.
