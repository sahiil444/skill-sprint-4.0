# Session 09: Type Safety in APIs, Pydantic Models & FastAPI Implementation

Welcome to **Session 09** of the Skill Sprint! This repository covers foundational and practical concepts of **Type Safety in APIs**, **Pydantic Data Validation & Modeling**, and **Production-Ready REST API Implementation using FastAPI**.

---

## 📑 Table of Contents

- [Overview & Objectives](#-overview--objectives)
- [Repository Structure](#-repository-structure)
- [Part 1: Type Safety in APIs](#-part-1-type-safety-in-apis)
- [Part 2: Core Pydantic Concepts (`Pydentic/`)](#-part-2-core-pydantic-concepts-pydentic)
  - [1. Why Pydantic & Field Annotations](#1-why-pydantic--field-annotations-01_why_pydenticpy)
  - [2. Custom Field Validation](#2-custom-field-validation-02_field_validatorpy)
  - [3. Cross-Field Model Validation](#3-cross-field-model-validation-03_model_validatorpy)
  - [4. Computed Fields](#4-computed-fields-04_computed_fieldpy)
  - [5. Nested Models](#5-nested-models-05_nested_modelpy)
  - [6. Model Serialization & Dumps](#6-model-serialization--dumps-06_serializationpy)
- [Part 3: FastAPI Implementation (`main1.py`)](#-part-3-fastapi-implementation-main1py)
  - [Schemas & Request Models](#schemas--request-models)
  - [Data Persistence (`patients.json`)](#data-persistence-patientsjson)
  - [API Endpoints & CRUD Operations](#api-endpoints--crud-operations)
- [Part 4: Running the Project](#-part-4-running-the-project)
- [API Documentation (Swagger & ReDoc)](#-interactive-api-documentation)

---

## 🎯 Overview & Objectives

In modern web development, APIs must be **predictable**, **robust**, and **type-safe**. Passing untyped dictionaries or loose parameters leads to silent runtime failures, insecure endpoints, and cumbersome manual data validation.

This session teaches:
1. **Type Safety & Type Annotations**: Catching data mismatches before they hit application logic.
2. **Pydantic V2**: Automated parsing, coercion, custom validators, computed properties, and serialization.
3. **FastAPI**: Declarative endpoint definition, automatic OpenAPI documentation, and native Pydantic schema validation.
4. **Persistent RESTful CRUD**: Building a complete Patient Management API powered by [main1.py](file:///c:/Users/moham/Desktop/skill-sprint-4.0/main1.py) and backed by [patients.json](file:///c:/Users/moham/Desktop/skill-sprint-4.0/patients.json).

---

## 📁 Repository Structure

```text
skill-sprint-4.0/
├── main1.py               # Complete FastAPI application with CRUD endpoints & Pydantic models
├── patients.json          # Persistent JSON datastore containing patient records
├── Pydentic/              # Step-by-step Pydantic learning modules
│   ├── 01_why_pydentic.py       # Data validation, type coercion, and Field constraints
│   ├── 02_field_validator.py    # Custom single-field validators and data transformations
│   ├── 03_model_validator.py    # Cross-field root validators
│   ├── 04_computed_field.py     # Dynamic/derived fields (e.g., BMI)
│   ├── 05_nested_model.py       # Hierarchical and nested data models
│   └── 06_serialization.py      # Model dumping, JSON serialization, and filtering
└── README.md              # Project documentation
```

---

## 🛡️ Part 1: Type Safety in APIs

### What is Type Safety?
Type safety ensures that data conforms to an expected contract (type, range, format) across all stages of execution. 

### Why is it Crucial in Web APIs?
- **Prevents Malformed Requests**: Invalid inputs (e.g. passing a string `"abc"` for `age` or negative values for `height`) are rejected immediately before business logic runs.
- **Auto-Generated Documentation**: Frameworks inspect type hints to build interactive OpenAPI schemas.
- **Enhanced Developer Experience (DX)**: Full autocomplete, static type checking (via mypy/pyright), and self-documenting code.
- **Standardized Error Responses**: Returning HTTP `422 Unprocessable Entity` with detailed error locations directly to the client.

---

## 🧩 Part 2: Core Pydantic Concepts (`Pydentic/`)

The [`Pydentic/`](file:///c:/Users/moham/Desktop/skill-sprint-4.0/Pydentic) folder contains progressive demonstrations of Pydantic V2 capabilities:

### 1. Why Pydantic & Field Annotations ([`01_why_pydentic.py`](file:///c:/Users/moham/Desktop/skill-sprint-4.0/Pydentic/01_why_pydentic.py))
- Demonstrates how Pydantic parses dictionaries, converts compatible types automatically (e.g. `'30'` into integer `30`), and raises `ValidationError` for incompatible types.
- Uses `Annotated` and `Field(...)` for setting metadata and strict constraints:
  - Numeric ranges: `gt=0`, `lt=120`
  - Strict typing: `strict=True`
  - Specialized types: `EmailStr`, `AnyUrl`, `Optional[List[str]]`, `Dict[str, str]`

```python
from pydantic import BaseModel, EmailStr, AnyUrl, Field
from typing import List, Dict, Optional, Annotated

class Patient(BaseModel):
    name: Annotated[str, Field(max_length=50, examples=['Nitish', 'Amit'])]
    email: EmailStr
    linkedin_url: AnyUrl
    age: int = Field(gt=0, lt=120)
    weight: Annotated[float, Field(gt=0, strict=True)]
    married: Annotated[bool, Field(default=None)]
    allergies: Annotated[Optional[List[str]], Field(default=None, max_length=5)]
    contact_details: Dict[str, str]
```

### 2. Custom Field Validation ([`02_field_validator.py`](file:///c:/Users/moham/Desktop/skill-sprint-4.0/Pydentic/02_field_validator.py))
- Demonstrates `@field_validator` for inspecting and transforming individual attributes.
- **Domain Whitelisting**: Restricting email domains (e.g., only accepting `@hdfc.com` or `@icici.com`).
- **Data Sanitization**: Transforming strings (e.g., auto-capitalizing patient names via `.upper()`).
- **Validation Timing**: Running validation logic `mode='after'` (default, after core parsing).

```python
@field_validator('email')
@classmethod
def email_validator(cls, value):
    valid_domains = ['hdfc.com', 'icici.com']
    domain_name = value.split('@')[-1]
    if domain_name not in valid_domains:
        raise ValueError('Not a valid domain')
    return value

@field_validator('name')
@classmethod
def transform_name(cls, value):
    return value.upper()
```

### 3. Cross-Field Model Validation ([`03_model_validator.py`](file:///c:/Users/moham/Desktop/skill-sprint-4.0/Pydentic/03_model_validator.py))
- Uses `@model_validator(mode='after')` to inspect relationships between multiple fields on the validated instance (`self`).
- **Business Rule**: If a patient is older than 60 (`self.age > 60`), an `'emergency'` contact key is mandatory inside `self.contact_details`.

```python
@model_validator(mode='after')
def validate_emergency_contact(self):
    if self.age > 60 and 'emergency' not in self.contact_details:
        raise ValueError('Patients older than 60 must have an emergency contact')
    return self
```

### 4. Computed Fields ([`04_computed_field.py`](file:///c:/Users/moham/Desktop/skill-sprint-4.0/Pydentic/04_computed_field.py))
- Uses `@computed_field` with `@property` to calculate derived values dynamically on serialization without requiring the client to pass them in.
- **BMI Calculation Formula**: $\text{BMI} = \frac{\text{weight}}{(\text{height})^2}$ rounded to 2 decimal places.

```python
@computed_field
@property
def bmi(self) -> float:
    return round(self.weight / (self.height ** 2), 2)
```

### 5. Nested Models ([`05_nested_model.py`](file:///c:/Users/moham/Desktop/skill-sprint-4.0/Pydentic/05_nested_model.py))
- Demonstrates composing schemas by nesting one `BaseModel` inside another.
- Maps nested dictionaries cleanly into hierarchical Python objects:

```python
class Address(BaseModel):
    city: str
    state: str
    pin: str

class Patient(BaseModel):
    name: str
    gender: str
    age: int
    address: Address
```

### 6. Model Serialization & Dumps ([`06_serialization.py`](file:///c:/Users/moham/Desktop/skill-sprint-4.0/Pydentic/06_serialization.py))
- Converts Pydantic model instances into Python dictionaries or JSON strings:
  - `model.model_dump()`: Returns standard Python `dict`.
  - `model.model_dump_json()`: Returns a JSON-formatted `str`.
  - `include={...}` / `exclude={...}`: Selective field inclusion/exclusion.
  - `exclude_unset=True`: Exports only fields explicitly passed during instantiation (critical for HTTP `PATCH`/partial updates).

---

## 🚀 Part 3: FastAPI Implementation ([`main1.py`](file:///c:/Users/moham/Desktop/skill-sprint-4.0/main1.py))

[`main1.py`](file:///c:/Users/moham/Desktop/skill-sprint-4.0/main1.py) integrates Pydantic models directly with FastAPI routes to build a RESTful Patient Management System.

### Schemas & Request Models

#### 1. Full Patient Schema (`Patient`)
Used when creating a new patient record. Includes strict field validation, allowed literals, and auto-computed BMI.

```python
class Patient(BaseModel):
    id: str
    name: str
    age: int = Field(gt=0, lt=120)
    gender: Literal["male", "female", "others"]
    height: float = Field(gt=0)
    weight: float = Field(gt=0)

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)
```

#### 2. Partial Update Schema (`PatientUpdate`)
All fields are optional (`None` default) to permit updating any subset of patient attributes.

```python
class PatientUpdate(BaseModel):
    name: str | None = None
    age: int | None = Field(default=None, gt=0, lt=120)
    gender: Literal["male", "female", "others"] | None = None
    height: float | None = Field(default=None, gt=0)
    weight: float | None = Field(default=None, gt=0)
```

---

### Data Persistence ([`patients.json`](file:///c:/Users/moham/Desktop/skill-sprint-4.0/patients.json))

Data is stored as a key-value dictionary of patient objects indexed by their unique ID (`P001`, `P002`, etc.):

```json
{
    "P001": {
        "name": "sumit",
        "city": "lakhimpur",
        "age": 28,
        "gender": "female",
        "height": 1.72,
        "weight": 90.0,
        "bmi": 30.42,
        "verdict": "Obese"
    }
}
```

Helper functions in [`main1.py`](file:///c:/Users/moham/Desktop/skill-sprint-4.0/main1.py):
- `load_data()`: Reads and parses `patients.json`.
- `save_data(data)`: Serializes and writes back updated data with formatting.

---

### API Endpoints & CRUD Operations

| Method | Endpoint | Description | Request Body | Response Codes |
| :--- | :--- | :--- | :--- | :--- |
| **GET** | `/` | API Health / Welcome message | *None* | `200 OK` |
| **GET** | `/patients` | Retrieve all registered patients | *None* | `200 OK` |
| **GET** | `/patients/{patient_id}` | Retrieve single patient by ID | *None* | `200 OK`, `404 Not Found` |
| **POST** | `/patients` | Create a new patient record | `Patient` (JSON) | `201 Created`, `400 Bad Request`, `422 Unprocessable Entity` |
| **PUT** | `/patients/{patient_id}` | Update existing patient details | `PatientUpdate` (JSON) | `200 OK`, `404 Not Found`, `422 Unprocessable Entity` |
| **DELETE** | `/patients/{patient_id}` | Remove a patient record | *None* | `200 OK`, `404 Not Found` |

#### Endpoint Highlights from [`main1.py`](file:///c:/Users/moham/Desktop/skill-sprint-4.0/main1.py):

- **Creating a Patient (`POST /patients`)**:
  Validates incoming JSON against `Patient`. Checks if the patient ID already exists; if not, dumps the model excluding the ID (since ID acts as the top-level dictionary key in storage) and writes to disk.
- **Updating a Patient (`PUT /patients/{patient_id}`)**:
  Extracts only the modified attributes using `patient_update.model_dump(exclude_unset=True)`. Merges them into existing patient data, runs validation through `Patient(**existing_patient)` to ensure constraints hold, automatically recalculates `bmi`, and commits to `patients.json`.
- **Deleting a Patient (`DELETE /patients/{patient_id}`)**:
  Verifies the record exists, removes the entry with `del data[patient_id]`, and returns confirmation.

---

## 💻 Part 4: Running the Project

### 1. Prerequisites & Dependencies
Ensure Python 3.10+ is installed. Install required packages:

```bash
pip install fastapi uvicorn "pydantic[email]"
```

### 2. Run the Pydantic Demonstration Scripts
Run each script independently from the root directory:

```bash
python Pydentic/01_why_pydentic.py
python Pydentic/02_field_validator.py
python Pydentic/03_model_validator.py
python Pydentic/04_computed_field.py
python Pydentic/05_nested_model.py
python Pydentic/06_serialization.py
```

### 3. Start the FastAPI Application
Launch the dev server using Uvicorn targeting [`main1.py`](file:///c:/Users/moham/Desktop/skill-sprint-4.0/main1.py):

```bash
uvicorn main1:app --reload
```

The application will start at: `http://127.0.0.1:8000`

---

## 📖 Interactive API Documentation

Once the server is running, FastAPI provides auto-generated API interfaces:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (Interactive testing & parameter documentation)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) (Clean, structured technical documentation)

These documentation pages are created directly from the Pydantic type definitions in [`main1.py`](file:///c:/Users/moham/Desktop/skill-sprint-4.0/main1.py), illustrating the full power of type safety in modern Python APIs.
