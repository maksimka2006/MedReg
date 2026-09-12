import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from config import APP_NAME, APPOINTMENT_STATUSES, DATE_FORMAT, SEX_VALUES
from services import AppointmentService, DoctorService, PatientService
from validators import validate_date


class MedRegApp(tk.Tk):
    def __init__(
        self,
        patient_service: PatientService,
        doctor_service: DoctorService,
        appointment_service: AppointmentService,
    ) -> None:
        super().__init__()

        self.patient_service = patient_service
        self.doctor_service = doctor_service
        self.appointment_service = appointment_service

        self.title(APP_NAME)
        self.geometry("1200x720")
        self.minsize(1100, 650)

        self._build_menu()
        self._build_widgets()
        self.refresh_all()

    def _build_menu(self) -> None:
        menu = tk.Menu(self)

        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Обновить все", command=self.refresh_all)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.destroy)

        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(label="О программе", command=self._show_about)

        menu.add_cascade(label="Файл", menu=file_menu)
        menu.add_cascade(label="Справка", menu=help_menu)

        self.config(menu=menu)

    def _build_widgets(self) -> None:
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self._build_patients_tab()
        self._build_doctors_tab()
        self._build_appointments_tab()
        self._build_reports_tab()

    def _build_patients_tab(self) -> None:
        frame = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(frame, text="Пациенты")

        top = ttk.LabelFrame(frame, text="Поиск и действия", padding=6)
        top.pack(fill=tk.X, pady=(0, 8))

        self.patient_search_var = tk.StringVar()
        ttk.Label(top, text="Поиск:").pack(side=tk.LEFT)
        entry = ttk.Entry(top, textvariable=self.patient_search_var, width=40)
        entry.pack(side=tk.LEFT, padx=4)
        entry.bind("<Return>", lambda event: self.refresh_patients())

        ttk.Button(top, text="Найти", command=self.refresh_patients).pack(
            side=tk.LEFT, padx=3
        )
        ttk.Button(top, text="Добавить", command=self.add_patient).pack(
            side=tk.LEFT, padx=3
        )
        ttk.Button(top, text="Изменить", command=self.edit_patient).pack(
            side=tk.LEFT, padx=3
        )
        ttk.Button(top, text="Удалить", command=self.delete_patient).pack(
            side=tk.LEFT, padx=3
        )
        ttk.Button(top, text="Обновить", command=self.refresh_patients).pack(
            side=tk.LEFT, padx=3
        )

        columns = (
            "id",
            "last_name",
            "first_name",
            "middle_name",
            "birth_date",
            "sex",
            "phone",
            "policy_number",
            "address",
        )

        headings = {
            "id": ("ID", 50),
            "last_name": ("Фамилия", 120),
            "first_name": ("Имя", 110),
            "middle_name": ("Отчество", 120),
            "birth_date": ("Дата рождения", 110),
            "sex": ("Пол", 50),
            "phone": ("Телефон", 130),
            "policy_number": ("Полис ОМС", 150),
            "address": ("Адрес", 260),
        }

        self.patient_tree = self._create_tree(frame, columns, headings)
        self.patient_tree.bind("<Double-1>", lambda event: self.edit_patient())

    def _build_doctors_tab(self) -> None:
        frame = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(frame, text="Врачи")

        top = ttk.LabelFrame(frame, text="Поиск и действия", padding=6)
        top.pack(fill=tk.X, pady=(0, 8))

        self.doctor_search_var = tk.StringVar()
        ttk.Label(top, text="Поиск:").pack(side=tk.LEFT)
        entry = ttk.Entry(top, textvariable=self.doctor_search_var, width=40)
        entry.pack(side=tk.LEFT, padx=4)
        entry.bind("<Return>", lambda event: self.refresh_doctors())

        ttk.Button(top, text="Найти", command=self.refresh_doctors).pack(
            side=tk.LEFT, padx=3
        )
        ttk.Button(top, text="Добавить", command=self.add_doctor).pack(
            side=tk.LEFT, padx=3
        )
        ttk.Button(top, text="Изменить", command=self.edit_doctor).pack(
            side=tk.LEFT, padx=3
        )
        ttk.Button(top, text="Деактивировать", command=self.delete_doctor).pack(
            side=tk.LEFT, padx=3
        )
        ttk.Button(top, text="Обновить", command=self.refresh_doctors).pack(
            side=tk.LEFT, padx=3
        )

        columns = ("id", "full_name", "specialty", "room", "phone", "active")

        headings = {
            "id": ("ID", 50),
            "full_name": ("ФИО врача", 260),
            "specialty": ("Специальность", 180),
            "room": ("Кабинет", 80),
            "phone": ("Телефон", 130),
            "active": ("Активен", 80),
        }

        self.doctor_tree = self._create_tree(frame, columns, headings)
        self.doctor_tree.bind("<Double-1>", lambda event: self.edit_doctor())

    def _build_appointments_tab(self) -> None:
        frame = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(frame, text="Запись на прием")

        top = ttk.LabelFrame(frame, text="Фильтры и действия", padding=6)
        top.pack(fill=tk.X, pady=(0, 8))

        self.appointment_search_var = tk.StringVar()
        self.appointment_date_var = tk.StringVar()
        self.appointment_status_var = tk.StringVar(value="Все")

        ttk.Label(top, text="Поиск:").pack(side=tk.LEFT)
        ttk.Entry(top, textvariable=self.appointment_search_var, width=25).pack(
            side=tk.LEFT, padx=3
        )

        ttk.Label(top, text="Дата:").pack(side=tk.LEFT, padx=(8, 0))
        ttk.Entry(top, textvariable=self.appointment_date_var, width=12).pack(
            side=tk.LEFT, padx=3
        )

        ttk.Label(top, text="Статус:").pack(side=tk.LEFT, padx=(8, 0))
        ttk.Combobox(
            top,
            textvariable=self.appointment_status_var,
            values=("Все",) + APPOINTMENT_STATUSES,
            state="readonly",
            width=15,
        ).pack(side=tk.LEFT, padx=3)

        ttk.Button(top, text="Найти", command=self.refresh_appointments).pack(
            side=tk.LEFT, padx=3
        )
        ttk.Button(top, text="Добавить", command=self.add_appointment).pack(
            side=tk.LEFT, padx=3
        )
        ttk.Button(top, text="Изменить", command=self.edit_appointment).pack(
            side=tk.LEFT, padx=3
        )
        ttk.Button(top, text="Удалить", command=self.delete_appointment).pack(
            side=tk.LEFT, padx=3
        )
        ttk.Button(top, text="Обновить", command=self.refresh_appointments).pack(
            side=tk.LEFT, padx=3
        )

        columns = (
            "id",
            "appointment_datetime",
            "status",
            "patient_name",
            "doctor_name",
            "specialty",
            "room",
            "reason",
            "notes",
        )

        headings = {
            "id": ("ID", 50),
            "appointment_datetime": ("Дата и время", 140),
            "status": ("Статус", 110),
            "patient_name": ("Пациент", 220),
            "doctor_name": ("Врач", 220),
            "specialty": ("Специальность", 160),
            "room": ("Каб.", 60),
            "reason": ("Причина", 180),
            "notes": ("Примечание", 180),
        }

        self.appointment_tree = self._create_tree(frame, columns, headings)
        self.appointment_tree.bind(
            "<Double-1>",
            lambda event: self.edit_appointment(),
        )

    def _build_reports_tab(self) -> None:
        frame = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(frame, text="Отчет")

        top = ttk.LabelFrame(frame, text="Отчет по записям на дату", padding=6)
        top.pack(fill=tk.X, pady=(0, 8))

        self.report_date_var = tk.StringVar(value=datetime.now().strftime(DATE_FORMAT))

        ttk.Label(top, text="Дата:").pack(side=tk.LEFT)
        ttk.Entry(top, textvariable=self.report_date_var, width=14).pack(
            side=tk.LEFT, padx=4
        )

        ttk.Button(top, text="Сформировать", command=self.generate_report).pack(
            side=tk.LEFT, padx=4
        )

        self.report_text = tk.Text(frame, wrap=tk.WORD)
        self.report_text.pack(fill=tk.BOTH, expand=True)

    def _create_tree(self, parent, columns, headings):
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True)

        tree = ttk.Treeview(container, columns=columns, show="headings")
        yscroll = ttk.Scrollbar(container, orient=tk.VERTICAL, command=tree.yview)
        xscroll = ttk.Scrollbar(container, orient=tk.HORIZONTAL, command=tree.xview)

        tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

        tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")

        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        for column in columns:
            text, width = headings[column]
            tree.heading(column, text=text)
            tree.column(column, width=width, anchor=tk.W)

        return tree

    def refresh_all(self) -> None:
        self.refresh_patients()
        self.refresh_doctors()
        self.refresh_appointments()
        self.generate_report()

    def refresh_patients(self) -> None:
        self._clear_tree(self.patient_tree)

        for row in self.patient_service.list(self.patient_search_var.get()):
            self.patient_tree.insert(
                "",
                tk.END,
                values=(
                    row["id"],
                    row["last_name"],
                    row["first_name"],
                    row["middle_name"],
                    row["birth_date"],
                    row["sex"],
                    row["phone"],
                    row["policy_number"],
                    row["address"],
                ),
            )

    def refresh_doctors(self) -> None:
        self._clear_tree(self.doctor_tree)

        for row in self.doctor_service.list(
            self.doctor_search_var.get(),
            include_inactive=True,
        ):
            self.doctor_tree.insert(
                "",
                tk.END,
                values=(
                    row["id"],
                    row["full_name"],
                    row["specialty"],
                    row["room"],
                    row["phone"],
                    "Да" if row["active"] else "Нет",
                ),
            )

    def refresh_appointments(self) -> None:
        self._clear_tree(self.appointment_tree)

        try:
            rows = self.appointment_service.list(
                search=self.appointment_search_var.get(),
                date_filter=self.appointment_date_var.get().strip(),
                status_filter=self.appointment_status_var.get(),
            )
        except Exception as exc:
            messagebox.showerror("Ошибка фильтра", str(exc))
            return

        for row in rows:
            self.appointment_tree.insert(
                "",
                tk.END,
                values=(
                    row["id"],
                    row["appointment_datetime"],
                    row["status"],
                    row["patient_name"],
                    row["doctor_name"],
                    row["specialty"],
                    row["room"],
                    row["reason"],
                    row["notes"],
                ),
            )

    def generate_report(self) -> None:
        self.report_text.delete("1.0", tk.END)

        try:
            date_value = validate_date(self.report_date_var.get())
            rows = self.appointment_service.list(date_filter=date_value)
        except Exception as exc:
            self.report_text.insert(tk.END, f"Ошибка формирования отчета: {exc}")
            return

        self.report_text.insert(
            tk.END,
            f"ОТЧЕТ ПО ЗАПИСЯМ НА ПРИЕМ ЗА {date_value}\n",
        )
        self.report_text.insert(tk.END, "=" * 60 + "\n\n")

        if not rows:
            self.report_text.insert(tk.END, "На выбранную дату записей нет.\n")
            return

        for index, row in enumerate(rows, start=1):
            self.report_text.insert(
                tk.END,
                (
                    f"{index}. {row['appointment_datetime']} | "
                    f"{row['status']} | "
                    f"{row['patient_name']} | "
                    f"{row['doctor_name']} ({row['specialty']}), "
                    f"каб. {row['room']} | "
                    f"{row['reason']}\n"
                ),
            )

    def add_patient(self) -> None:
        dialog = PatientDialog(self)
        self.wait_window(dialog)

        if dialog.result:
            try:
                self.patient_service.create(dialog.result)
                self.refresh_patients()
                self.refresh_appointments()
            except Exception as exc:
                messagebox.showerror("Ошибка", str(exc))

    def edit_patient(self) -> None:
        patient_id = self._selected_id(self.patient_tree)

        if patient_id is None:
            return

        patient = self.patient_service.get(patient_id)
        dialog = PatientDialog(self, patient)
        self.wait_window(dialog)

        if dialog.result:
            try:
                self.patient_service.update(patient_id, dialog.result)
                self.refresh_patients()
                self.refresh_appointments()
            except Exception as exc:
                messagebox.showerror("Ошибка", str(exc))

    def delete_patient(self) -> None:
        patient_id = self._selected_id(self.patient_tree)

        if patient_id is None:
            return

        if not messagebox.askyesno(
            "Подтверждение",
            "Удалить пациента? Связанные записи на прием также будут удалены.",
        ):
            return

        try:
            self.patient_service.delete(patient_id)
            self.refresh_patients()
            self.refresh_appointments()
        except Exception as exc:
            messagebox.showerror("Ошибка", str(exc))

    def add_doctor(self) -> None:
        dialog = DoctorDialog(self)
        self.wait_window(dialog)

        if dialog.result:
            try:
                self.doctor_service.create(dialog.result)
                self.refresh_doctors()
            except Exception as exc:
                messagebox.showerror("Ошибка", str(exc))

    def edit_doctor(self) -> None:
        doctor_id = self._selected_id(self.doctor_tree)

        if doctor_id is None:
            return

        doctor = self.doctor_service.get(doctor_id)
        dialog = DoctorDialog(self, doctor)
        self.wait_window(dialog)

        if dialog.result:
            try:
                self.doctor_service.update(doctor_id, dialog.result)
                self.refresh_doctors()
                self.refresh_appointments()
            except Exception as exc:
                messagebox.showerror("Ошибка", str(exc))

    def delete_doctor(self) -> None:
        doctor_id = self._selected_id(self.doctor_tree)

        if doctor_id is None:
            return

        if not messagebox.askyesno("Подтверждение", "Деактивировать врача?"):
            return

        try:
            self.doctor_service.delete(doctor_id)
            self.refresh_doctors()
        except Exception as exc:
            messagebox.showerror("Ошибка", str(exc))

    def add_appointment(self) -> None:
        dialog = AppointmentDialog(
            self,
            self.patient_service,
            self.doctor_service,
        )
        self.wait_window(dialog)

        if dialog.result:
            try:
                self.appointment_service.create(dialog.result)
                self.refresh_appointments()
                self.generate_report()
            except Exception as exc:
                messagebox.showerror("Ошибка", str(exc))

    def edit_appointment(self) -> None:
        appointment_id = self._selected_id(self.appointment_tree)

        if appointment_id is None:
            return

        appointment = self.appointment_service.get(appointment_id)
        dialog = AppointmentDialog(
            self,
            self.patient_service,
            self.doctor_service,
            appointment,
        )
        self.wait_window(dialog)

        if dialog.result:
            try:
                self.appointment_service.update(appointment_id, dialog.result)
                self.refresh_appointments()
                self.generate_report()
            except Exception as exc:
                messagebox.showerror("Ошибка", str(exc))

    def delete_appointment(self) -> None:
        appointment_id = self._selected_id(self.appointment_tree)

        if appointment_id is None:
            return

        if not messagebox.askyesno("Подтверждение", "Удалить запись на прием?"):
            return

        try:
            self.appointment_service.delete(appointment_id)
            self.refresh_appointments()
            self.generate_report()
        except Exception as exc:
            messagebox.showerror("Ошибка", str(exc))

    def _clear_tree(self, tree: ttk.Treeview) -> None:
        for item in tree.get_children():
            tree.delete(item)

    def _selected_id(self, tree: ttk.Treeview):
        selected = tree.selection()

        if not selected:
            messagebox.showwarning("Выбор записи", "Выберите запись в таблице.")
            return None

        values = tree.item(selected[0], "values")
        return int(values[0])

    def _show_about(self) -> None:
        messagebox.showinfo(
            "О программе",
            "MedReg\nСистема учета пациентов и записи на прием\n"
            "Python + SQLite + Tkinter",
        )


class BaseDialog(tk.Toplevel):
    def __init__(self, parent, title: str) -> None:
        super().__init__(parent)
        self.result = None
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _add_buttons(self, row: int) -> None:
        frame = ttk.Frame(self)
        frame.grid(row=row, column=0, columnspan=2, sticky="e", padx=8, pady=8)

        ttk.Button(frame, text="Сохранить", command=self._save).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(frame, text="Отмена", command=self.destroy).pack(
            side=tk.LEFT, padx=4
        )

    def _center(self) -> None:
        self.update_idletasks()
        parent = self.master
        x = parent.winfo_rootx() + 80
        y = parent.winfo_rooty() + 80
        self.geometry(f"+{x}+{y}")

    def _save(self) -> None:
        raise NotImplementedError


class PatientDialog(BaseDialog):
    def __init__(self, parent, data=None) -> None:
        super().__init__(parent, "Пациент")
        data = data or {}

        self.vars = {
            "last_name": tk.StringVar(value=data.get("last_name", "")),
            "first_name": tk.StringVar(value=data.get("first_name", "")),
            "middle_name": tk.StringVar(value=data.get("middle_name", "")),
            "birth_date": tk.StringVar(value=data.get("birth_date", "")),
            "sex": tk.StringVar(value=data.get("sex", "М")),
            "phone": tk.StringVar(value=data.get("phone", "")),
            "policy_number": tk.StringVar(value=data.get("policy_number", "")),
            "address": tk.StringVar(value=data.get("address", "")),
        }

        labels = [
            ("Фамилия*", "last_name"),
            ("Имя*", "first_name"),
            ("Отчество", "middle_name"),
            ("Дата рождения* (ДД-ММ-ГГГГ)", "birth_date"),
            ("Пол*", "sex"),
            ("Телефон* (+7XXXXXXXXXX)", "phone"),
            ("Полис ОМС* (16 цифр)", "policy_number"),
            ("Адрес", "address"),
        ]

        for row, (label, key) in enumerate(labels):
            ttk.Label(self, text=label).grid(
                row=row,
                column=0,
                sticky="w",
                padx=8,
                pady=4,
            )

            if key == "sex":
                widget = ttk.Combobox(
                    self,
                    textvariable=self.vars[key],
                    values=SEX_VALUES,
                    state="readonly",
                    width=37,
                )
            else:
                widget = ttk.Entry(self, textvariable=self.vars[key], width=40)

            widget.grid(row=row, column=1, sticky="ew", padx=8, pady=4)

        self._add_buttons(len(labels))
        self._center()

    def _save(self) -> None:
        self.result = {key: var.get() for key, var in self.vars.items()}
        self.destroy()


class DoctorDialog(BaseDialog):
    def __init__(self, parent, data=None) -> None:
        super().__init__(parent, "Врач")
        data = data or {}

        self.vars = {
            "full_name": tk.StringVar(value=data.get("full_name", "")),
            "specialty": tk.StringVar(value=data.get("specialty", "")),
            "room": tk.StringVar(value=data.get("room", "")),
            "phone": tk.StringVar(value=data.get("phone", "")),
        }

        labels = [
            ("ФИО врача*", "full_name"),
            ("Специальность*", "specialty"),
            ("Кабинет", "room"),
            ("Телефон", "phone"),
        ]

        for row, (label, key) in enumerate(labels):
            ttk.Label(self, text=label).grid(
                row=row,
                column=0,
                sticky="w",
                padx=8,
                pady=4,
            )
            ttk.Entry(self, textvariable=self.vars[key], width=45).grid(
                row=row,
                column=1,
                sticky="ew",
                padx=8,
                pady=4,
            )

        self._add_buttons(len(labels))
        self._center()

    def _save(self) -> None:
        self.result = {key: var.get() for key, var in self.vars.items()}
        self.destroy()


class AppointmentDialog(BaseDialog):
    def __init__(
        self,
        parent,
        patient_service: PatientService,
        doctor_service: DoctorService,
        data=None,
    ) -> None:
        super().__init__(parent, "Запись на прием")
        data = data or {}

        self.patient_service = patient_service
        self.doctor_service = doctor_service

        self.patient_items = self._patient_items()
        self.doctor_items = self._doctor_items()

        default_datetime = datetime.now().strftime("%Y-%m-%d %H:00")

        self.patient_var = tk.StringVar(
            value=self._find_item(self.patient_items, data.get("patient_id"))
        )
        self.doctor_var = tk.StringVar(
            value=self._find_item(self.doctor_items, data.get("doctor_id"))
        )

        self.vars = {
            "appointment_datetime": tk.StringVar(
                value=data.get("appointment_datetime", default_datetime)
            ),
            "status": tk.StringVar(value=data.get("status", "Запланирован")),
            "reason": tk.StringVar(value=data.get("reason", "")),
            "notes": tk.StringVar(value=data.get("notes", "")),
        }

        row = 0

        ttk.Label(self, text="Пациент*").grid(
            row=row,
            column=0,
            sticky="w",
            padx=8,
            pady=4,
        )
        ttk.Combobox(
            self,
            textvariable=self.patient_var,
            values=self.patient_items,
            state="readonly",
            width=75,
        ).grid(row=row, column=1, sticky="ew", padx=8, pady=4)

        row += 1
        ttk.Label(self, text="Врач*").grid(
            row=row,
            column=0,
            sticky="w",
            padx=8,
            pady=4,
        )
        ttk.Combobox(
            self,
            textvariable=self.doctor_var,
            values=self.doctor_items,
            state="readonly",
            width=75,
        ).grid(row=row, column=1, sticky="ew", padx=8, pady=4)

        row += 1
        ttk.Label(self, text="Дата и время*").grid(
            row=row,
            column=0,
            sticky="w",
            padx=8,
            pady=4,
        )
        ttk.Entry(
            self,
            textvariable=self.vars["appointment_datetime"],
            width=30,
        ).grid(row=row, column=1, sticky="w", padx=8, pady=4)

        row += 1
        ttk.Label(self, text="Статус*").grid(
            row=row,
            column=0,
            sticky="w",
            padx=8,
            pady=4,
        )
        ttk.Combobox(
            self,
            textvariable=self.vars["status"],
            values=APPOINTMENT_STATUSES,
            state="readonly",
            width=25,
        ).grid(row=row, column=1, sticky="w", padx=8, pady=4)

        row += 1
        ttk.Label(self, text="Причина").grid(
            row=row,
            column=0,
            sticky="w",
            padx=8,
            pady=4,
        )
        ttk.Entry(self, textvariable=self.vars["reason"], width=70).grid(
            row=row,
            column=1,
            sticky="ew",
            padx=8,
            pady=4,
        )

        row += 1
        ttk.Label(self, text="Примечание").grid(
            row=row,
            column=0,
            sticky="w",
            padx=8,
            pady=4,
        )
        ttk.Entry(self, textvariable=self.vars["notes"], width=70).grid(
            row=row,
            column=1,
            sticky="ew",
            padx=8,
            pady=4,
        )

        self._add_buttons(row + 1)
        self._center()

    def _patient_items(self):
        items = []

        for patient in self.patient_service.list():
            middle = f" {patient['middle_name']}" if patient["middle_name"] else ""
            items.append(
                f"{patient['id']} | {patient['last_name']} "
                f"{patient['first_name']}{middle}, "
                f"{patient['birth_date']}, полис {patient['policy_number']}"
            )

        return items

    def _doctor_items(self):
        items = []

        for doctor in self.doctor_service.list():
            items.append(
                f"{doctor['id']} | {doctor['full_name']}, "
                f"{doctor['specialty']}, каб. {doctor['room']}"
            )

        return items

    def _find_item(self, items, entity_id):
        if not items:
            return ""

        if not entity_id:
            return items[0]

        prefix = f"{entity_id} |"

        for item in items:
            if item.startswith(prefix):
                return item

        return items[0]

    def _extract_id(self, value: str, field_name: str) -> int:
        if not value or "|" not in value:
            raise ValueError(f"Выберите значение поля «{field_name}».")

        return int(value.split("|", 1)[0].strip())

    def _save(self) -> None:
        try:
            patient_id = self._extract_id(self.patient_var.get(), "Пациент")
            doctor_id = self._extract_id(self.doctor_var.get(), "Врач")
        except ValueError as exc:
            messagebox.showerror("Ошибка ввода", str(exc), parent=self)
            return

        self.result = {
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "appointment_datetime": self.vars["appointment_datetime"].get(),
            "status": self.vars["status"].get(),
            "reason": self.vars["reason"].get(),
            "notes": self.vars["notes"].get(),
        }

        self.destroy()