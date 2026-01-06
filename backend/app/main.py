from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

app = FastAPI()

# -----------------------
# CORS
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# MODELS
# -----------------------
class Patient(BaseModel):
    id: int
    name: str
    age: int
    disease: str

class PatientCreate(BaseModel):
    name: str
    age: int
    disease: str


class Doctor(BaseModel):
    id: int
    name: str
    specialty: str

class DoctorCreate(BaseModel):
    name: str
    specialty: str


class Appointment(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    date: str
    time: str
    status: str  # Scheduled | Completed | Cancelled

class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    date: str
    time: str


# ✅ STATUS UPDATE MODEL (🔥 FIX)
class AppointmentStatusUpdate(BaseModel):
    status: str


class PatientHistory(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    diagnosis: str
    prescription: str
    notes: str
    visit_date: date

class PatientHistoryCreate(BaseModel):
    patient_id: int
    doctor_id: int
    diagnosis: str
    prescription: str
    notes: str
    visit_date: date


class LoginRequest(BaseModel):
    username: str
    password: str


# -----------------------
# FAKE DATABASES
# -----------------------
patients_db: List[Patient] = []

doctors_db: List[Doctor] = [
    Doctor(id=1, name="Dr Ahmed", specialty="General"),
    Doctor(id=2, name="Dr Sara", specialty="Skin"),
    Doctor(id=3, name="Dr Ali", specialty="Heart"),
]

appointments_db: List[Appointment] = []
patient_history_db: List[PatientHistory] = []

next_patient_id = 1
next_appointment_id = 1
next_history_id = 1

# -----------------------
# ROOT
# -----------------------
@app.get("/")
def root():
    return {"status": "Backend running perfectly 🚀"}

# -----------------------
# PATIENTS
# -----------------------
@app.get("/patients/")
def get_patients():
    return patients_db

@app.post("/patients/")
def add_patient(patient: PatientCreate):
    global next_patient_id
    new_patient = Patient(id=next_patient_id, **patient.dict())
    patients_db.append(new_patient)
    next_patient_id += 1
    return new_patient

@app.put("/patients/{patient_id}")
def update_patient(patient_id: int, patient: PatientCreate):
    for i, p in enumerate(patients_db):
        if p.id == patient_id:
            patients_db[i] = Patient(id=patient_id, **patient.dict())
            return patients_db[i]
    raise HTTPException(status_code=404, detail="Patient not found")

@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int):
    for i, p in enumerate(patients_db):
        if p.id == patient_id:
            patients_db.pop(i)
            return {"success": True}
    raise HTTPException(status_code=404, detail="Patient not found")

# -----------------------
# DOCTORS
# -----------------------
@app.get("/doctors/")
def get_doctors():
    return doctors_db

@app.post("/doctors/")
def add_doctor(doctor: DoctorCreate):
    new_id = max([d.id for d in doctors_db], default=0) + 1
    new_doctor = Doctor(id=new_id, **doctor.dict())
    doctors_db.append(new_doctor)
    return new_doctor

# -----------------------
# APPOINTMENTS
# -----------------------
@app.get("/appointments/")
def get_appointments():
    return appointments_db


@app.post("/appointments/")
def add_appointment(appt: AppointmentCreate):
    global next_appointment_id, next_history_id

    patient = next((p for p in patients_db if p.id == appt.patient_id), None)
    doctor = next((d for d in doctors_db if d.id == appt.doctor_id), None)

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # ❌ DOUBLE BOOKING CHECK
    for a in appointments_db:
        if (
            a.doctor_id == appt.doctor_id
            and a.date == appt.date
            and a.time == appt.time
            and a.status == "Scheduled"
        ):
            raise HTTPException(
                status_code=400,
                detail="Doctor already booked for this time"
            )

    new_appt = Appointment(
        id=next_appointment_id,
        status="Scheduled",
        **appt.dict()
    )
    appointments_db.append(new_appt)

    # 🔥 AUTO HISTORY
    history = PatientHistory(
        id=next_history_id,
        patient_id=patient.id,
        doctor_id=doctor.id,
        diagnosis=patient.disease,
        prescription="Pending",
        notes="Appointment scheduled",
        visit_date=date.fromisoformat(appt.date),
    )
    patient_history_db.append(history)

    next_appointment_id += 1
    next_history_id += 1

    return new_appt


# ✅🔥 FIXED STATUS UPDATE ENDPOINT
@app.put("/appointments/{appointment_id}/status")
def update_appointment_status(
    appointment_id: int,
    data: AppointmentStatusUpdate
):
    for a in appointments_db:
        if a.id == appointment_id:
            a.status = data.status
            return a

    raise HTTPException(status_code=404, detail="Appointment not found")


# -----------------------
# DOCTOR SCHEDULE
# -----------------------
@app.get("/schedule/doctor/{doctor_id}")
def doctor_schedule(doctor_id: int, date: Optional[str] = None):
    data = [a for a in appointments_db if a.doctor_id == doctor_id]
    if date:
        data = [a for a in data if a.date == date]
    return data

# -----------------------
# HISTORY
# -----------------------
@app.get("/history/")
def get_all_history():
    return patient_history_db

@app.get("/history/{patient_id}")
def get_patient_history(patient_id: int):
    return [h for h in patient_history_db if h.patient_id == patient_id]

# -----------------------
# LOGIN
# -----------------------
@app.post("/login")
def login(data: LoginRequest):
    if data.username == "Ejaz" and data.password == "Ejaz3021":
        return {"success": True}
    raise HTTPException(status_code=401, detail="Invalid credentials")
