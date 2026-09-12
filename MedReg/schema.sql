PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    last_name TEXT NOT NULL,
    first_name TEXT NOT NULL,
    middle_name TEXT DEFAULT '',
    birth_date TEXT NOT NULL,
    sex TEXT NOT NULL CHECK (sex IN ('М', 'Ж')),
    phone TEXT NOT NULL,
    policy_number TEXT NOT NULL UNIQUE,
    address TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_patients_name
ON patients(last_name, first_name, middle_name);

CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    specialty TEXT NOT NULL,
    room TEXT DEFAULT '',
    phone TEXT DEFAULT '',
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at TEXT,
    UNIQUE(full_name, specialty, room)
);

CREATE INDEX IF NOT EXISTS idx_doctors_specialty
ON doctors(specialty);

CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    appointment_datetime TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Запланирован'
        CHECK (status IN ('Запланирован', 'Завершен', 'Отменен', 'Неявка')),
    reason TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at TEXT,
    FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY(doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_appointments_datetime
ON appointments(appointment_datetime);

CREATE UNIQUE INDEX IF NOT EXISTS ux_appointments_doctor_datetime_active
ON appointments(doctor_id, appointment_datetime)
WHERE status <> 'Отменен';

CREATE UNIQUE INDEX IF NOT EXISTS ux_appointments_patient_datetime_active
ON appointments(patient_id, appointment_datetime)
WHERE status <> 'Отменен';

DROP VIEW IF EXISTS appointment_view;

CREATE VIEW appointment_view AS
SELECT
    a.id,
    a.patient_id,
    a.doctor_id,
    a.appointment_datetime,
    a.status,
    a.reason,
    a.notes,
    p.last_name || ' ' || p.first_name || ' ' || IFNULL(p.middle_name, '') AS patient_name,
    p.policy_number,
    p.phone AS patient_phone,
    d.full_name AS doctor_name,
    d.specialty,
    d.room,
    a.created_at,
    a.updated_at
FROM appointments a
JOIN patients p ON p.id = a.patient_id
JOIN doctors d ON d.id = a.doctor_id;

INSERT OR IGNORE INTO doctors
(id, full_name, specialty, room, phone, active)
VALUES
(1, 'Иванов Сергей Петрович', 'Терапевт', '201', '+78212000001', 1),
(2, 'Петрова Анна Викторовна', 'Кардиолог', '305', '+78212000002', 1),
(3, 'Сидоров Павел Николаевич', 'Хирург', '110', '+78212000003', 1),
(4, 'Кузнецова Мария Андреевна', 'Невролог', '214', '+78212000004', 1);

INSERT OR IGNORE INTO patients
(id, last_name, first_name, middle_name, birth_date, sex, phone, policy_number, address)
VALUES
(1, 'Смирнова', 'Елена', 'Игоревна', '12-04-1988', 'Ж', '+79120000001', '1111222233334444', 'г. Сыктывкар, ул. Ленина, д. 1'),
(2, 'Козлов', 'Андрей', 'Сергеевич', '25-10-1975', 'М', '+79120000002', '2222333344445555', 'г. Сыктывкар, ул. Коммунистическая, д. 10'),
(3, 'Морозова', 'Ольга', 'Павловна', '03-07-1992', 'Ж', '+79120000003', '3333444455556666', 'г. Сыктывкар, ул. Советская, д. 5');

INSERT OR IGNORE INTO appointments
(id, patient_id, doctor_id, appointment_datetime, status, reason, notes)
VALUES
(1, 1, 1, '2026-06-24 09:00', 'Запланирован', 'Первичный прием', ''),
(2, 2, 2, '2026-06-24 10:30', 'Запланирован', 'Консультация кардиолога', '');