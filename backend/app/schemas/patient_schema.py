from pydantic import BaseModel

class PatientBase(BaseModel):
    name: str
    phone: str
    address: str
    age: int

class PatientCreate(PatientBase):
    pass

class PatientResponse(PatientBase):
    id: int

    class Config:
        orm_mode = True
