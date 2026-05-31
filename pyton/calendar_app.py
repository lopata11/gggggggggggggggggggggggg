import tkinter as tk
from tkinter import messagebox, scrolledtext
import calendar
import json
import os
from datetime import datetime

class CalendarNoteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📅 Календарь с заметками")
        self.root.geometry("850x650")
        self.root.minsize(800, 600)

        # Текущая дата
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.selected_date = None

        # Файл хранения
        self.notes_file = "calendar_notes.json"
        self.notes = self._load_notes()

        self._setup_ui()
        self._render_calendar()

    def _load_notes(self):
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                messagebox.showwarning("Ошибка", "Файл заметок повреждён. Создан новый.")
        return {}

    def _save_notes_to_file(self):
        with open(self.notes_file, 'w', encoding='utf-8') as f:
            json.dump(self.notes, f, ensure_ascii=False, indent=2)

    def _setup_ui(self):
        # --- Навигация ---
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(fill=tk.X, pady=10)

        self.prev_btn = tk.Button(nav_frame, text="◀ Пред.", font=("Arial", 10), command=self._prev_month)
        self.prev_btn.pack(side=tk.LEFT, padx=15)

        self.month_label = tk.Label(nav_frame, text="", font=("Arial", 16, "bold"))
        self.month_label.pack(side=tk.LEFT, expand=True)

        self.next_btn = tk.Button(nav_frame, text="След. ▶", font=("Arial", 10), command=self._next_month)
        self.next_btn.pack(side=tk.RIGHT, padx=15)

        # --- Календарная сетка ---
        self.grid_container = tk.Frame(self.root)
        self.grid_container.pack(pady=5)

        # Заголовки дней недели
        days_header = tk.Frame(self.grid_container)
        days_header.pack(fill=tk.X)
        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for i, day in enumerate(days):
            tk.Label(days_header, text=day, width=10, font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=0, column=i, padx=1, pady=2)

        # Фрейм для кнопок дней (будет перерисовываться)
        self.days_grid = tk.Frame(self.grid_container)
        self.days_grid.pack()

        # --- Блок заметок ---
        note_frame = tk.Frame(self.root, padx=20, pady=10)
        note_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(note_frame, text="📝 Заметка:", font=("Arial", 12, "bold")).pack(anchor=tk.W)

        self.note_text = scrolledtext.ScrolledText(note_frame, height=10, font=("Consolas", 11), wrap=tk.WORD)
        self.note_text.pack(fill=tk.BOTH, expand=True, pady=5)

        btn_frame = tk.Frame(note_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(btn_frame, text="💾 Сохранить", bg="#4CAF50", fg="white", font=("Arial", 10), command=self._save_note).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🗑 Удалить", bg="#f44336", fg="white", font=("Arial", 10), command=self._delete_note).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📋 Очистить поле", font=("Arial", 10), command=self._clear_note_field).pack(side=tk.RIGHT, padx=5)

    def _render_calendar(self):
        # Очистка старых кнопок
        for widget in self.days_grid.winfo_children():
            widget.destroy()

        # Названия месяцев на русском
        month_names = [
            "", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]
        self.month_label.config(text=f"{month_names[self.current_month]} {self.current_year}")

        # Генерация сетки
        cal = calendar.Calendar(firstweekday=calendar.MONDAY)
        month_days = cal.monthdayscalendar(self.current_year, self.current_month)

        for row_idx, week in enumerate(month_days, start=1):
            for col_idx, day in enumerate(week):
                if day == 0:
                    continue  # Пропускаем пустые ячейки

                date_key = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
                
                # Определение цвета
                bg_color = "#ffffff"
                if date_key in self.notes and self.notes[date_key].strip():
                    bg_color = "#fff9c4"  # Жёлтый, если есть заметка
                if date_key == self.selected_date:
                    bg_color = "#bbdefb"  # Синий, если выбран

                btn = tk.Button(
                    self.days_grid, text=str(day), width=10, height=2,
                    font=("Arial", 11), bg=bg_color, relief="raised",
                    command=lambda d=date_key: self._select_date(d)
                )
                btn.grid(row=row_idx, column=col_idx, padx=2, pady=2)

    def _select_date(self, date_key):
        self.selected_date = date_key
        # Загружаем заметку или оставляем пустым
        current_note = self.notes.get(date_key, "")
        self.note_text.delete(1.0, tk.END)
        self.note_text.insert(tk.END, current_note)
        self._render_calendar()

    def _save_note(self):
        if not self.selected_date:
            messagebox.showwarning("Внимание", "Сначала выберите дату в календаре!")
            return

        text = self.note_text.get(1.0, tk.END).strip()
        if text:
            self.notes[self.selected_date] = text
            messagebox.showinfo("Успех", f"Заметка сохранена на {self.selected_date}")
        else:
            # Если текст пустой, удаляем запись (опционально)
            self.notes.pop(self.selected_date, None)
            messagebox.showinfo("Успех", "Пустая заметка удалена")

        self._save_notes_to_file()
        self._render_calendar()

    def _delete_note(self):
        if not self.selected_date:
            messagebox.showwarning("Внимание", "Сначала выберите дату!")
            return

        if self.selected_date in self.notes:
            del self.notes[self.selected_date]
            self._save_notes_to_file()
            self.note_text.delete(1.0, tk.END)
            self._render_calendar()
            messagebox.showinfo("Успех", f"Заметка за {self.selected_date} удалена")
        else:
            messagebox.showinfo("Информация", "Заметка для этой даты уже отсутствует.")

    def _clear_note_field(self):
        self.note_text.delete(1.0, tk.END)

    def _prev_month(self):
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.selected_date = None
        self.note_text.delete(1.0, tk.END)
        self._render_calendar()

    def _next_month(self):
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self.selected_date = None
        self.note_text.delete(1.0, tk.END)
        self._render_calendar()


if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarNoteApp(root)
    root.mainloop()