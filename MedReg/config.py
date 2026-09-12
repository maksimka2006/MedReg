from pathlib import Path

APP_NAME = "MedReg - система учета пациентов и записи на прием"

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "hospital.db"

DATE_FORMAT = "%d-%m-%Y"
DATETIME_FORMAT = "%d-%m-%Y %H:%M"

SEX_VALUES = ("М", "Ж")
APPOINTMENT_STATUSES = ("Запланирован", "Завершен", "Отменен", "Неявка")