from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Patient:
    id: Optional[int]
    last_name: str
    first_name: str
    middle_name: str
    birth_date: str
    sex: str
    phone: str
    policy_number: str
    address: str


@dataclass(frozen=True)
class Doctor:
    id: Optional[int]
    full_name: str
    specialty: str
    room: str
    phone: str
    active: int = 1


@dataclass(frozen=True)
class Appointment:
    id: Optional[int]
    patient_id: int
    doctor_id: int
    appointment_datetime: str
    status: str
    reason: str
    notes: str