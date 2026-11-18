"""Command line expense tracker (data stored in a CSV file).

The file emma_expenses.csv shipped with the project already contains a full
year of expenses, so the statistics are meaningful from the first run.
"""

import csv
import os
import math
from datetime import datetime

FILENAME = "emma_expenses.csv"  # or "personnal_expenses.csv"
COLUMNS = ["date", "category", "description", "amount"]

"""Rate maximum d'endettement pour simulation de crédits dans le code."""
MAX_DEBT_RATIO = 0.35


class Expense:
    """One expense, with its values already converted to the right type.

    A CSV file only stores text, so the amount arrives as "68.72" and not as a
    number: the conversion is done once, here.
    """

    def __init__(self, date, category, description, amount):
        self.date = date  # kept as text, e.g. "05/03/2025"
        self.category = category
        self.description = description
        self.amount = float(amount)

    def to_row(self):
        """Return the expense as a list of texts, ready to be written in the CSV."""
        return [self.date, self.category, self.description, f"{self.amount:.2f}"]


def read_expenses():
    """Return the list of expenses saved in the CSV file."""
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
    """Append one expense at the end of the CSV file."""
    file_exists = os.path.exists(FILENAME)

    with open(FILENAME, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # A brand new file needs its header line first.
        if not file_exists:
            writer.writerow(COLUMNS)

        writer.writerow(expense.to_row())


def get_month_key(expense):
    day, month, year = expense.date.split("/")
    return f"{month}/{year}"


def count_month(expenses):
    months = set()

    for expense in expenses:
        months.add(get_month_key(expense))

    return len(months)


def get_total(expenses):

    total = 0
    for expense in expenses:
        total += expense.amount
    return total


def total_by_category(expenses):
    counts = {}

    for expense in expenses:
        """retire les espaces et met les catégories en majuscule"""
        category = expense.category.strip().upper()
        """grab la category dans le dictionnaire et renvoie sa valeur, sinon 0, puis ajoute le montant de la dépense lue"""
        counts[category] = counts.get(category, 0) + expense.amount 
    return counts

def monthly_average(expenses):
    if not expenses:
        return
    average = get_total(expenses)/count_month(expenses)
    return average


def ask_amount(prompt, allow_zero=False):
    """Fonction à appeler pour demander un montant dans les fonctionnalités intégrées, exclu directement l'entrée 0 ou négative"""
    answer = input(prompt).strip().replace(",", ".")

    """Gestion des entrées de caractères."""
    try:
        amount = float(answer)
    except ValueError:
        print("Error: Invalid Entry.\n")
        return None

    """Gestion des entrées négatives ou égales à 0."""
    if not math.isfinite(amount) or amount < 0 or (amount == 0 and not allow_zero):
        print("Error: Value is out of range.\n")
        return None

    return amount


def car_savings_simulation():
    expenses = read_expenses()
    income = ask_amount("Enter your monthly net income: ")

    if income is None:
        return

    car_price = ask_amount("Enter the price of the car you're willing to buy: ")
    if income is None:
        return

    savings = income - monthly_average(expenses)
    if savings <= 0:
        print("Not enough savings capacity: the project cannot be financed.\n")
        return
    else:
        print(f"Monthly savings available: {savings:.2f}")
        months_needed = math.ceil(car_price/savings)
        print(f"Months needed to buy the car: {months_needed}")


def get_housing_monthly(expenses):
    """Retourne la dépense moyenne dans la catégorie HOUSING ou rien si il n'y en a pas"""
    total_housing = total_by_category(expenses)

    if "HOUSING" not in total_housing:
        print("No housing expense found, add one first. \n")
        return None
    return total_housing["HOUSING"] / count_month(expenses)


def house_mortgage_simulation():
    """Simulation d'un emprunt immobilier"""
    expenses = read_expenses()

    if not expenses:
        print("No expense saved yet, add one first. \n")
        return
    
    income = ask_amount("Enter your monthly net income: ")
    if income is None:
        return
    
    annual_rate = ask_amount("Enter the annual interest rate (%): ", allow_zero=True)
    if annual_rate is None:
        return

    years = ask_amount("Enter the loan duration (years): ")
    if years is None:
        return

    housing_monthly = get_housing_monthly(expenses)
    if housing_monthly is None:
        print("No housing savings capacity: the project cannot be financed.\n")
        return

    savings = income - monthly_average(expenses)
    if savings <= 0:
        print("Not enough savings capacity: the project cannot be financed.\n")
        return

    theoretical_payment = savings + housing_monthly
    payment = min(theoretical_payment, income * MAX_DEBT_RATIO)

    n = years * 12
    r = annual_rate / 100 / 12

    if r == 0:
        capital = payment * n
    else:
        capital = payment * (1 - (1 + r) ** (-n)) / r

    print(f"Monthly housing expense: {housing_monthly:.2f}")
    print(f"Monthly savings available: {savings:.2f}")
    print(f"Retained monthly payment: {payment:.2f}")
    print(f"Estimated borrowing capacity: {capital:.2f}")
        

def show_history():
    """Display every saved expense along with the total."""
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

def show_statistics():
    """Affiche l'ensemble des statistiques du compte"""
    expenses = read_expenses()

    if not expenses:
        print("No expense save yet, add one first. \n")
        return
    
    print("--- Statistics ---")
    print(f"Expenses total: {get_total(expenses):.2f}.")
    print(f"Number of months: {count_month(expenses)}.")
    print(f"Monthly Average: {monthly_average(expenses):.2f}.")

    totals = total_by_category(expenses)
    months = count_month(expenses)

    print(f"\n{'Category':<20}{'Total:':>12}{'Monthly Average:':>18}")
    for category, total in totals.items():
        average = total/months
        print(f"{category:<20}{total:>12.2f}{average:>18.2f}")
    print()


def add_expense():
    """Ask for the details of an expense and append it to the CSV file."""
    category = input("Category (e.g. groceries, transport): ").strip()
    description = input("Description: ").strip()

    # In French a comma is used for decimals, but Python needs a dot.
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
    """Display the available choices."""
    print("=== Expense tracker ===")
    print("1. Show history")
    print("2. Add an expense")
    print("3. Show Statistics")
    print("4. Car Savings Simulation")
    print("5. House Mortgage Simulation")
    print("6. Quit")


def main():
    while True:
        show_menu()
        choice = input("Your choice: ").strip()

        if choice == "1":
            show_history()
        elif choice == "2":
            add_expense()
        elif choice == "3":
            show_statistics()
        elif choice == "4":
            car_savings_simulation()
        elif choice == "5":
            house_mortgage_simulation()
        elif choice == "6":
            print("See you soon!")
            break
        else:
            print("Invalid choice, please enter a number between 1 and 6.\n")


if __name__ == "__main__":
    main()