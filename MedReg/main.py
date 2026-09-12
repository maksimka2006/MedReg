from app import MedRegApp
from database import DatabaseManager
from services import AppointmentService, DoctorService, PatientService


def main() -> None:
    db = DatabaseManager()
    db.initialize()

    patient_service = PatientService(db)
    doctor_service = DoctorService(db)
    appointment_service = AppointmentService(db)

    app = MedRegApp(
        patient_service=patient_service,
        doctor_service=doctor_service,
        appointment_service=appointment_service,
    )
    app.mainloop()


if __name__ == "__main__":
    main()