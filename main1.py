from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Literal
import json

app = FastAPI()


# ==================== PATIENT MODEL ====================

class Patient(BaseModel):
    id: str
    name: str
    age: int = Field(gt=0, lt=120)
    gender: Literal["male", "female", "others"]
    height: float = Field(gt=0)
    weight: float = Field(gt=0)

    # Calculate BMI automatically
    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)


# ==================== PATIENT UPDATE MODEL ====================

class PatientUpdate(BaseModel):
    name: str | None = None
    age: int | None = Field(default=None, gt=0, lt=120)
    gender: Literal["male", "female", "others"] | None = None
    height: float | None = Field(default=None, gt=0)
    weight: float | None = Field(default=None, gt=0)


# ==================== LOAD AND SAVE DATA ====================

def load_data():
    with open("patients.json", "r") as file:
        return json.load(file)


def save_data(data):
    with open("patients.json", "w") as file:
        json.dump(data, file, indent=4)


# ==================== HOME ====================

@app.get("/")
def home():
    return {"message": "Patient Management System"}


# ==================== VIEW ALL PATIENTS ====================

@app.get("/patients")
def view_patients():
    return load_data()


# ==================== VIEW ONE PATIENT ====================

@app.get("/patients/{patient_id}")
def view_patient(patient_id: str):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return data[patient_id]


# ==================== CREATE PATIENT ====================

@app.post("/patients")
def create_patient(patient: Patient):

    data = load_data()

    if patient.id in data:
        raise HTTPException(
            status_code=400,
            detail="Patient already exists"
        )

    data[patient.id] = patient.model_dump(exclude={"id"})

    save_data(data)

    return JSONResponse(
        status_code=201,
        content={"message": "Patient created successfully"}
    )


# ==================== UPDATE PATIENT ====================

@app.put("/patients/{patient_id}")
def update_patient(patient_id: str, patient_update: PatientUpdate):

    data = load_data()

    if patient_id not in data:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    # Get existing patient details
    existing_patient = data[patient_id].copy()

    # Get only the fields provided by the user
    updated_data = patient_update.model_dump(exclude_unset=True)

    # Update the provided fields
    for key, value in updated_data.items():
        existing_patient[key] = value

    # Add patient ID for validation
    existing_patient["id"] = patient_id

    # Validate updated data and recalculate BMI
    patient = Patient(**existing_patient)

    # Convert patient object into dictionary
    data[patient_id] = patient.model_dump(exclude={"id"})

    save_data(data)

    return JSONResponse(
        status_code=200,
        content={"message": "Patient updated successfully"}
    )


# ==================== DELETE PATIENT ====================

@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: str):

    data = load_data()

    if patient_id not in data:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    del data[patient_id]

    save_data(data)

    return JSONResponse(
        status_code=200,
        content={"message": "Patient deleted successfully"}
    )