from sqlalchemy.orm import Session
from app.models.patient import Patient                 # <--- Change required here
from app.schemas.patient_schema import PatientCreate

def get_all_patients(db: Session):
    return db.query(Patient).all()

def create_patient(db: Session, patient_data: PatientCreate):
    # .dict() is deprecated in Pydantic V2, use .model_dump() instead, 
    # but using .dict() for compatibility with older Pydantic version
    new_patient = Patient(**patient_data.dict())
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

def delete_patient(db: Session, patient_id: int):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if patient:
        db.delete(patient)
        db.commit()
        return True
    return False