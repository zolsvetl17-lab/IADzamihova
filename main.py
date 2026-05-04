import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.expenses = []
        self.load_data()
        
        self.create_widgets()
    
    def create_widgets(self):
        # Поля ввода
        tk.Label(self.root, text="Сумма:").grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = tk.Entry(self.root)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(self.root, text="Категория:").grid(row=1, column=0, padx=5, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            self.root,
            textvariable=self.category_var,
            values=["Еда", "Транспорт", "Развлечения", "Жильё", "Прочее"]
        )
        self.category_combo.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(self.root, text="Дата (ГГГГ-ММ-ДД):").grid(row=2, column=0, padx=5, pady=5)
        self.date_entry = tk.Entry(self.root)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Кнопка добавления
        tk.Button(self.root, text="Добавить расход", command=self.add_expense).grid(
            row=3, column=0, columnspan=2, pady=10
        )
        # Таблица
        self.tree = ttk.Treeview(self.root, columns=("Сумма", "Категория", "Дата"), show="headings")
        self.tree.heading("Сумма", text="Сумма")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Дата", text="Дата")
        self.tree.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        # Фильтры
        tk.Label(self.root, text="Фильтр по категории:").grid(row=5, column=0, padx=5, pady=5)
        self.filter_category_var = tk.StringVar()
        self.filter_category_combo = ttk.Combobox(
            self.root,
            textvariable=self.filter_category_var,
            values=["Все", "Еда", "Транспорт", "Развлечения", "Жильё", "Прочее"]
        )
        self.filter_category_combo.set("Все")
        self.filter_category_combo.grid(row=5, column=1, padx=5, pady=5)
        tk.Label(self.root, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=6, column=0, padx=5, pady=5)
        self.filter_date_entry = tk.Entry(self.root)
        self.filter_date_entry.grid(row=6, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Применить фильтры", command=self.apply_filters).grid(
            row=7, column=0, columnspan=2, pady=5
        )
        # Подсчёт суммы за период
        tk.Label(self.root, text="Период (ГГГГ-ММ-ДД - ГГГГ-ММ-ДД):").grid(row=8, column=0, padx=5, pady=5)
        self.period_entry = tk.Entry(self.root)
        self.period_entry.grid(row=8, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Посчитать сумму за период", command=self.calculate_period_sum).grid(
            row=9, column=0, columnspan=2, pady=5
        )
        self.sum_label = tk.Label(self.root, text="Общая сумма: 0")
        self.sum_label.grid(row=10, column=0, columnspan=2, pady=5)
    def validate_input(self):
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат суммы")
            return False
        try:
            datetime.strptime(self.date_entry.get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат даты (используйте ГГГГ-ММ-ДД)")
            return False
        if not self.category_var.get():
            messagebox.showerror("Ошибка", "Выберите категорию")
            return False
        return True

    def add_expense(self):
        if not self.validate_input():
            return
        expense = {
            "amount": float(self.amount_entry.get()),
            "category": self.category_var.get(),
            "date": self.date_entry.get()
        }
        self.expenses.append(expense)
        self.update_table()
        self.save_data()
        # Очистка полей
        self.amount_entry.delete(0, tk.END)
        self.category_var.set("")
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for expense in self.expenses:
            self.tree.insert("", "end", values=(
                expense["amount"],
                expense["category"],
                expense["date"]
            ))

    def save_data(self):
        with open("expenses.json", "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=2)

    def load_data(self):
        if os.path.exists("expenses.json"):
            with open("expenses.json", "r", encoding="utf-8") as f:
                self.expenses = json.load(f)
        else:
            self.expenses = []

    def apply_filters(self):
        filtered = self.expenses
        # Фильтр по категории
        category = self.filter_category_var.get()
        if category != "Все":
            filtered = [e for e in filtered if e["category"] == category]
        # Фильтр по дате
        date_filter = self.filter_date_entry.get()
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
                filtered = [
                    e for e in filtered
                    if datetime.strptime(e["date"], "%Y-%m-%d").date() == filter_date
                ]
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректный формат даты фильтра")
                return
        self.update_filtered_table(filtered)

    def update_filtered_table(self, expenses):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for expense in expenses:
            self.tree.insert("", "end", values=(
                expense["amount"],
                expense["category"],
                expense["date"]
            ))

    def calculate_period_sum(self):
        period_text = self.period_entry.get()
        if not period_text:
            messagebox.showerror("Ошибка", "Введите период в формате ГГГГ-ММ-ДД - ГГГГ-ММ-ДД")
            return

        try:
            start_str, end_str = period_text.split(" - ")
            start_date = datetime.strptime(start_str.strip(), "%Y-%m-%d").date()
            end_date = datetime.strptime(end_str.strip(), "%Y-%m-%d").date()

            if start_date > end_date:
                messagebox.showerror("Ошибка", "Начальная дата не может быть позже конечной")
                return

            total = sum(
                e["amount"] for e in self.expenses
                if start_date <= datetime.strptime(e["date"], "%Y-%m-%d").date() <= end_date
            )
            self.sum_label.config(text=f"Общая сумма за период: {total}")
        except ValueError:
            messagebox.showerror(
                "Ошибка",
                "Некорректный формат периода. Используйте ГГГГ-ММ-ДД - ГГГГ-ММ-ДД"
            )

# Основной блок запуска приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
