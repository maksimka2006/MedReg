import sqlite3
from typing import Any, Dict, List, Optional

from database import DatabaseManager
from validators import (
    validate_appointment_data,
    validate_date,
    validate_doctor_data,
    validate_patient_data,
    validate_status,
)


class ServiceError(RuntimeError):
    """Ошибка бизнес-логики приложения."""


class PatientService:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def create(self, data: Dict[str, Any]) -> int:
        patient = validate_patient_data(data)

        try:
            return self.db.execute(
                """
                INSERT INTO patients
                (last_name, first_name, middle_name, birth_date, sex,
                 phone, policy_number, address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    patient["last_name"],
                    patient["first_name"],
                    patient["middle_name"],
                    patient["birth_date"],
                    patient["sex"],
                    patient["phone"],
                    patient["policy_number"],
                    patient["address"],
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise ServiceError("Пациент с таким полисом ОМС уже существует.") from exc

    def update(self, patient_id: int, data: Dict[str, Any]) -> None:
        if not self.get(patient_id):
            raise ServiceError("Пациент не найден.")

        patient = validate_patient_data(data)

        try:
            self.db.execute(
                """
                UPDATE patients
                SET last_name = ?,
                    first_name = ?,
                    middle_name = ?,
                    birth_date = ?,
                    sex = ?,
                    phone = ?,
                    policy_number = ?,
                    address = ?,
                    updated_at = datetime('now', 'localtime')
                WHERE id = ?
                """,
                (
                    patient["last_name"],
                    patient["first_name"],
                    patient["middle_name"],
                    patient["birth_date"],
                    patient["sex"],
                    patient["phone"],
                    patient["policy_number"],
                    patient["address"],
                    patient_id,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise ServiceError("Пациент с таким полисом ОМС уже существует.") from exc

    def delete(self, patient_id: int) -> None:
        if not self.get(patient_id):
            raise ServiceError("Пациент не найден.")

        self.db.execute("DELETE FROM patients WHERE id = ?", (patient_id,))

    def get(self, patient_id: int) -> Optional[Dict[str, Any]]:
        return self.db.fetch_one(
            "SELECT * FROM patients WHERE id = ?",
            (patient_id,),
        )

    def list(self, search: str = "") -> List[Dict[str, Any]]:
        search = (search or "").strip()

        if search:
            pattern = f"%{search}%"
            return self.db.fetch_all(
                """
                SELECT *
                FROM patients
                WHERE last_name LIKE ?
                   OR first_name LIKE ?
                   OR middle_name LIKE ?
                   OR phone LIKE ?
                   OR policy_number LIKE ?
                ORDER BY last_name, first_name, middle_name
                """,
                (pattern, pattern, pattern, pattern, pattern),
            )

        return self.db.fetch_all(
            """
            SELECT *
            FROM patients
            ORDER BY last_name, first_name, middle_name
            """
        )


class DoctorService:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def create(self, data: Dict[str, Any]) -> int:
        doctor = validate_doctor_data(data)

        try:
            return self.db.execute(
                """
                INSERT INTO doctors
                (full_name, specialty, room, phone, active)
                VALUES (?, ?, ?, ?, 1)
                """,
                (
                    doctor["full_name"],
                    doctor["specialty"],
                    doctor["room"],
                    doctor["phone"],
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise ServiceError("Такой врач уже существует.") from exc

    def update(self, doctor_id: int, data: Dict[str, Any]) -> None:
        if not self.get(doctor_id):
            raise ServiceError("Врач не найден.")

        doctor = validate_doctor_data(data)

        try:
            self.db.execute(
                """
                UPDATE doctors
                SET full_name = ?,
                    specialty = ?,
                    room = ?,
                    phone = ?,
                    updated_at = datetime('now', 'localtime')
                WHERE id = ?
                """,
                (
                    doctor["full_name"],
                    doctor["specialty"],
                    doctor["room"],
                    doctor["phone"],
                    doctor_id,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise ServiceError("Такой врач уже существует.") from exc

    def delete(self, doctor_id: int) -> None:
        if not self.get(doctor_id):
            raise ServiceError("Врач не найден.")

        self.db.execute(
            """
            UPDATE doctors
            SET active = 0,
                updated_at = datetime('now', 'localtime')
            WHERE id = ?
            """,
            (doctor_id,),
        )

    def get(self, doctor_id: int) -> Optional[Dict[str, Any]]:
        return self.db.fetch_one(
            "SELECT * FROM doctors WHERE id = ?",
            (doctor_id,),
        )

    def list(
        self,
        search: str = "",
        include_inactive: bool = False,
    ) -> List[Dict[str, Any]]:
        search = (search or "").strip()
        conditions = []
        params: List[Any] = []

        if not include_inactive:
            conditions.append("active = 1")

        if search:
            pattern = f"%{search}%"
            conditions.append("(full_name LIKE ? OR specialty LIKE ? OR room LIKE ?)")
            params.extend([pattern, pattern, pattern])

        where_sql = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        return self.db.fetch_all(
            f"""
            SELECT *
            FROM doctors
            {where_sql}
            ORDER BY active DESC, specialty, full_name
            """,
            params,
        )


class AppointmentService:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def create(self, data: Dict[str, Any]) -> int:
        appointment = validate_appointment_data(data)
        self._ensure_entities_exist(appointment["patient_id"], appointment["doctor_id"])
        self._check_conflicts(
            appointment["patient_id"],
            appointment["doctor_id"],
            appointment["appointment_datetime"],
        )

        try:
            return self.db.execute(
                """
                INSERT INTO appointments
                (patient_id, doctor_id, appointment_datetime,
                 status, reason, notes)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    appointment["patient_id"],
                    appointment["doctor_id"],
                    appointment["appointment_datetime"],
                    appointment["status"],
                    appointment["reason"],
                    appointment["notes"],
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise ServiceError("Невозможно создать запись: обнаружен конфликт.") from exc

    def update(self, appointment_id: int, data: Dict[str, Any]) -> None:
        if not self.get(appointment_id):
            raise ServiceError("Запись на прием не найдена.")

        appointment = validate_appointment_data(data)
        self._ensure_entities_exist(appointment["patient_id"], appointment["doctor_id"])
        self._check_conflicts(
            appointment["patient_id"],
            appointment["doctor_id"],
            appointment["appointment_datetime"],
            exclude_id=appointment_id,
        )

        try:
            self.db.execute(
                """
                UPDATE appointments
                SET patient_id = ?,
                    doctor_id = ?,
                    appointment_datetime = ?,
                    status = ?,
                    reason = ?,
                    notes = ?,
                    updated_at = datetime('now', 'localtime')
                WHERE id = ?
                """,
                (
                    appointment["patient_id"],
                    appointment["doctor_id"],
                    appointment["appointment_datetime"],
                    appointment["status"],
                    appointment["reason"],
                    appointment["notes"],
                    appointment_id,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise ServiceError("Невозможно обновить запись: обнаружен конфликт.") from exc

    def delete(self, appointment_id: int) -> None:
        if not self.get(appointment_id):
            raise ServiceError("Запись на прием не найдена.")

        self.db.execute(
            "DELETE FROM appointments WHERE id = ?",
            (appointment_id,),
        )

    def get(self, appointment_id: int) -> Optional[Dict[str, Any]]:
        return self.db.fetch_one(
            "SELECT * FROM appointment_view WHERE id = ?",
            (appointment_id,),
        )

    def list(
        self,
        search: str = "",
        date_filter: str = "",
        status_filter: str = "",
    ) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM appointment_view WHERE 1 = 1"
        params: List[Any] = []

        if date_filter:
            date_value = validate_date(date_filter)
            sql += " AND substr(appointment_datetime, 1, 10) = ?"
            params.append(date_value)

        if status_filter and status_filter != "Все":
            validate_status(status_filter)
            sql += " AND status = ?"
            params.append(status_filter)

        if search:
            pattern = f"%{search.strip()}%"
            sql += """
                AND (
                    patient_name LIKE ?
                    OR doctor_name LIKE ?
                    OR specialty LIKE ?
                    OR reason LIKE ?
                )
            """
            params.extend([pattern, pattern, pattern, pattern])

        sql += " ORDER BY appointment_datetime DESC"

        return self.db.fetch_all(sql, params)

    def set_status(self, appointment_id: int, status: str) -> None:
        if not self.get(appointment_id):
            raise ServiceError("Запись на прием не найдена.")

        status = validate_status(status)

        try:
            self.db.execute(
                """
                UPDATE appointments
                SET status = ?,
                    updated_at = datetime('now', 'localtime')
                WHERE id = ?
                """,
                (status, appointment_id),
            )
        except sqlite3.IntegrityError as exc:
            raise ServiceError("Статус невозможно изменить из-за конфликта записи.") from exc

    def _ensure_entities_exist(self, patient_id: int, doctor_id: int) -> None:
        patient = self.db.fetch_one("SELECT id FROM patients WHERE id = ?", (patient_id,))
        doctor = self.db.fetch_one(
            "SELECT id FROM doctors WHERE id = ? AND active = 1",
            (doctor_id,),
        )

        if not patient:
            raise ServiceError("Выбранный пациент не найден.")

        if not doctor:
            raise ServiceError("Выбранный врач не найден или деактивирован.")

    def _check_conflicts(
        self,
        patient_id: int,
        doctor_id: int,
        appointment_datetime: str,
        exclude_id: Optional[int] = None,
    ) -> None:
        doctor_params: List[Any] = [doctor_id, appointment_datetime]
        patient_params: List[Any] = [patient_id, appointment_datetime]
        exclude_sql = ""

        if exclude_id:
            exclude_sql = " AND id <> ?"
            doctor_params.append(exclude_id)
            patient_params.append(exclude_id)

        doctor_conflict = self.db.fetch_one(
            f"""
            SELECT id
            FROM appointments
            WHERE doctor_id = ?
              AND appointment_datetime = ?
              AND status <> 'Отменен'
              {exclude_sql}
            """,
            doctor_params,
        )

        if doctor_conflict:
            raise ServiceError("У выбранного врача уже есть запись на это время.")

        patient_conflict = self.db.fetch_one(
            f"""
            SELECT id
            FROM appointments
            WHERE patient_id = ?
              AND appointment_datetime = ?
              AND status <> 'Отменен'
              {exclude_sql}
            """,
            patient_params,
        )

        if patient_conflict:
            raise ServiceError("Пациент уже записан на это время.")