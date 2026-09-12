import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database import DatabaseManager
from services import AppointmentService, DoctorService, PatientService, ServiceError


class ServicesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        file_descriptor, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(file_descriptor)

        self.db = DatabaseManager(self.db_path)
        self.db.initialize()

        self.patient_service = PatientService(self.db)
        self.doctor_service = DoctorService(self.db)
        self.appointment_service = AppointmentService(self.db)

    def tearDown(self) -> None:
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_create_patient(self) -> None:
        patient_id = self.patient_service.create(
            {
                "last_name": "Тестов",
                "first_name": "Иван",
                "middle_name": "Петрович",
                "birth_date": "01-01-1990",
                "sex": "М",
                "phone": "+79120001122",
                "policy_number": "9999888877776666",
                "address": "Тестовый адрес",
            }
        )

        patient = self.patient_service.get(patient_id)

        self.assertIsNotNone(patient)
        self.assertEqual(patient["last_name"], "Тестов")

    def test_duplicate_policy_rejected(self) -> None:
        data = {
            "last_name": "Тестова",
            "first_name": "Анна",
            "middle_name": "",
            "birth_date": "02-02-1991",
            "sex": "Ж",
            "phone": "+79120001123",
            "policy_number": "9999888877776666",
            "address": "",
        }

        self.patient_service.create(data)

        with self.assertRaises(ServiceError):
            self.patient_service.create(data)

    def test_create_appointment_and_detect_conflict(self) -> None:
        patient_id = self.patient_service.create(
            {
                "last_name": "Пациент",
                "first_name": "Тест",
                "middle_name": "",
                "birth_date": "05-05-1985",
                "sex": "М",
                "phone": "+79120001124",
                "policy_number": "1234567890123456",
                "address": "",
            }
        )

        doctor_id = self.doctor_service.create(
            {
                "full_name": "Врач Тестовый",
                "specialty": "Терапевт",
                "room": "500",
                "phone": "",
            }
        )

        appointment = {
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "appointment_datetime": "25-06-2026 10:00",
            "status": "Запланирован",
            "reason": "Проверка",
            "notes": "",
        }

        self.appointment_service.create(appointment)

        with self.assertRaises(ServiceError):
            self.appointment_service.create(appointment)


if __name__ == "__main__":
    unittest.main()