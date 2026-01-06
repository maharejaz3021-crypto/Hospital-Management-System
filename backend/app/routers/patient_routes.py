from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.patient_schema import PatientCreate, PatientResponse
from app.crud.patient_crud import get_all_patients, create_patient, delete_patient

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.get("/", response_model=list[PatientResponse])
def get_patients(db: Session = Depends(get_db)):
    return get_all_patients(db)

@router.post("/", response_model=PatientResponse)
def add_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    return create_patient(db, patient)

@router.delete("/{patient_id}")
def remove_patient(patient_id: int, db: Session = Depends(get_db)):
    return {"deleted": delete_patient(db, patient_id)}
