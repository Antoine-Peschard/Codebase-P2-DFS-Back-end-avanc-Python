import csv
import os
from datetime import datetime

FILENAME = "emma_expenses.csv"  # or "personnal_expenses.csv"
COLUMNS = ["date", "category", "description", "amount"]


class Expense:

    def __init__(self, date, category, description, amount):
        self.date = date  # kept as text, e.g. "05/03/2025"
        self.category = category
        self.description = description
        self.amount = float(amount)

    def to_row(self):
        return [self.date, self.category, self.description, f"{self.amount:.2f}"]


def read_expenses():
    if not os.path.exists(FILENAME):
        return []

    expenses = []

    with open(FILENAME, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        # Each row is a dictionary of texts: we turn it into an Expense.
        for row in reader:
            expense = Expense(
                row["date"], row["category"], row["description"], row["amount"]
            )
            expenses.append(expense)

    return expenses


def save_expense(expense):
    file_exists = os.path.exists(FILENAME)

    with open(FILENAME, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # A brand new file needs its header line first.
        if not file_exists:
            writer.writerow(COLUMNS)

        writer.writerow(expense.to_row())


def show_history():
    expenses = read_expenses()

    if not expenses:
        print("No expense saved yet, add one first.\n")
        return

    print("\n--- Expense history ---")
    header = f"{'Date':<12}{'Category':<20}{'Description':<30}{'Amount':>10}"
    print(header)

    total = 0
    for expense in expenses:
        line = (
            f"{expense.date:<12}{expense.category:<20}"
            f"{expense.description:<30}{expense.amount:>10.2f}"
        )
        print(line)
        total += expense.amount

    print(f"\nTotal: {total:.2f} EUR over {len(expenses)} expense(s).\n")


def add_expense():
    category = input("Category (e.g. groceries, transport): ").strip()
    description = input("Description: ").strip()

    answer = input("Amount in euros: ").strip().replace(",", ".")

    try:
        amount = float(answer)
    except ValueError:
        print("Invalid amount, the expense was not saved.\n")
        return

    today = datetime.now().strftime("%d/%m/%Y")
    expense = Expense(today, category, description, amount)
    save_expense(expense)

    print(f"Expense of {expense.amount:.2f} EUR saved.\n")


def show_menu():
    print("=== Expense tracker ===")
    print("1. Show history")
    print("2. Add an expense")
    print("3. Quit")


def main():
    while True:
        show_menu()
        choice = input("Your choice: ").strip()

        if choice == "1":
            show_history()
        elif choice == "2":
            add_expense()
        elif choice == "3":
            print("See you soon!")
            break
        else:
            print("Invalid choice, please enter a number between 1 and 3.\n")


if __name__ == "__main__":
    main()