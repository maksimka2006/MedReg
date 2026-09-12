import re
from datetime import datetime
from typing import Any, Dict, Mapping

from config import APPOINTMENT_STATUSES, DATE_FORMAT, DATETIME_FORMAT, SEX_VALUES


class ValidationError(ValueError):
    """Ошибка проверки пользовательских данных."""


def required(value: Any, field_name: str) -> str:
    if value is None or str(value).strip() == "":
        raise ValidationError(f"Поле «{field_name}» обязательно для заполнения.")
    return str(value).strip()


def optional_text(value: Any, max_length: int = 255) -> str:
    if value is None:
        return ""

    text = str(value).strip()

    if len(text) > max_length:
        raise ValidationError(
            f"Длина текста не должна превышать {max_length} символов."
        )

    return text


def validate_name(value: Any, field_name: str) -> str:
    text = required(value, field_name)

    if len(text) > 80:
        raise ValidationError(f"Поле «{field_name}» слишком длинное.")

    if not re.fullmatch(r"[А-Яа-яЁёA-Za-z.\-\s]+", text):
        raise ValidationError(
            f"Поле «{field_name}» должно содержать только буквы, пробелы, "
            "точки или дефисы."
        )

    return text


def normalize_phone(value: Any) -> str:
    text = required(value, "Телефон")
    phone = re.sub(r"[\s\-\(\)]", "", text)

    if phone.startswith("8") and len(phone) == 11 and phone[1:].isdigit():
        phone = "+7" + phone[1:]

    if phone.startswith("7") and len(phone) == 11 and phone.isdigit():
        phone = "+" + phone

    if not re.fullmatch(r"\+7\d{10}", phone):
        raise ValidationError(
            "Телефон должен быть указан в формате +7XXXXXXXXXX."
        )

    return phone


def validate_policy(value: Any) -> str:
    policy = re.sub(r"\D", "", required(value, "Полис ОМС"))

    if len(policy) != 16:
        raise ValidationError("Номер полиса ОМС должен содержать 16 цифр.")

    return policy


def validate_birth_date(value: Any) -> str:
    text = required(value, "Дата рождения")

    try:
        parsed_date = datetime.strptime(text, DATE_FORMAT).date()
    except ValueError as exc:
        raise ValidationError("Дата рождения должна быть в формате ДД-ММ-ГГГГ.") from exc

    if parsed_date > datetime.now().date():
        raise ValidationError("Дата рождения не может быть больше текущей даты.")

    return text


def validate_date(value: Any) -> str:
    text = required(value, "Дата")

    try:
        datetime.strptime(text, DATE_FORMAT)
    except ValueError as exc:
        raise ValidationError("Дата должна быть в формате ДД-ММ-ГГГГ.") from exc

    return text


def validate_datetime(value: Any) -> str:
    text = required(value, "Дата и время приема")

    try:
        parsed_datetime = datetime.strptime(text, DATETIME_FORMAT)
    except ValueError as exc:
        raise ValidationError(
            "Дата и время должны быть в формате ДД-ММ-ГГГГ ЧЧ:ММ."
        ) from exc

    if parsed_datetime.minute not in (0, 15, 30, 45):
        raise ValidationError("Минуты приема должны быть 00, 15, 30 или 45.")

    return text


def validate_sex(value: Any) -> str:
    sex = required(value, "Пол")

    if sex not in SEX_VALUES:
        raise ValidationError("Пол должен иметь значение «М» или «Ж».")

    return sex


def validate_status(value: Any) -> str:
    status = required(value, "Статус")

    if status not in APPOINTMENT_STATUSES:
        raise ValidationError("Недопустимый статус записи.")

    return status


def positive_int(value: Any, field_name: str) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"Поле «{field_name}» должно быть числом.") from exc

    if number <= 0:
        raise ValidationError(f"Поле «{field_name}» должно быть больше нуля.")

    return number


def validate_patient_data(data: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "last_name": validate_name(data.get("last_name"), "Фамилия"),
        "first_name": validate_name(data.get("first_name"), "Имя"),
        "middle_name": optional_text(data.get("middle_name"), 80),
        "birth_date": validate_birth_date(data.get("birth_date")),
        "sex": validate_sex(data.get("sex")),
        "phone": normalize_phone(data.get("phone")),
        "policy_number": validate_policy(data.get("policy_number")),
        "address": optional_text(data.get("address"), 255),
    }


def validate_doctor_data(data: Mapping[str, Any]) -> Dict[str, Any]:
    phone_raw = str(data.get("phone") or "").strip()

    return {
        "full_name": validate_name(data.get("full_name"), "ФИО врача"),
        "specialty": validate_name(data.get("specialty"), "Специальность"),
        "room": optional_text(data.get("room"), 20),
        "phone": normalize_phone(phone_raw) if phone_raw else "",
    }


def validate_appointment_data(data: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "patient_id": positive_int(data.get("patient_id"), "Пациент"),
        "doctor_id": positive_int(data.get("doctor_id"), "Врач"),
        "appointment_datetime": validate_datetime(data.get("appointment_datetime")),
        "status": validate_status(data.get("status") or "Запланирован"),
        "reason": optional_text(data.get("reason"), 200),
        "notes": optional_text(data.get("notes"), 500),
    }