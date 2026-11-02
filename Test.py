import json
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path


DATA_FILE = Path(__file__).with_name("expenses.json")


def load_expenses(file_path: Path = DATA_FILE) -> list[dict[str, str]]:
    if not file_path.exists():
        return []

    try:
        with file_path.open(encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(f"{file_path} contains invalid JSON.") from error

    if not isinstance(data, list):
        raise ValueError(f"{file_path} must contain a list of expenses.")

    expenses: list[dict[str, str]] = []
    for item in data:
        if not isinstance(item, dict):
            raise ValueError(f"{file_path} contains an invalid expense.")

        description = item.get("description")
        amount = item.get("amount")
        expense_date = item.get("date")
        if not isinstance(description, str) or not description.strip():
            raise ValueError(f"{file_path} contains an expense with no description.")
        if not isinstance(amount, str) or not isinstance(expense_date, str):
            raise ValueError(f"{file_path} contains an invalid expense.")

        try:
            parsed_amount = Decimal(amount)
            date.fromisoformat(expense_date)
        except (InvalidOperation, ValueError) as error:
            raise ValueError(f"{file_path} contains an invalid amount or date.") from error
        if not parsed_amount.is_finite() or parsed_amount <= 0:
            raise ValueError(f"{file_path} contains a non-positive expense amount.")

        expenses.append(
            {
                "description": description,
                "amount": amount,
                "date": expense_date,
            }
        )

    return expenses


def save_expenses(expenses: list[dict[str, str]], file_path: Path = DATA_FILE) -> None:
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(expenses, file, indent=2)
        file.write("\n")


def add_expense(expenses: list[dict[str, str]], file_path: Path = DATA_FILE) -> None:
    description = input("What was the expense for? ").strip()
    if not description:
        print("Description cannot be empty.")
        return

    amount_text = input("How much did it cost? ").strip()
    try:
        amount = Decimal(amount_text)
    except InvalidOperation:
        print("Please enter a valid amount, such as 12.50.")
        return

    if not amount.is_finite() or amount <= 0:
        print("Amount must be greater than zero.")
        return
    if amount.as_tuple().exponent < -2:
        print("Please enter no more than two decimal places.")
        return

    expense = {
        "description": description,
        "amount": str(amount),
        "date": date.today().isoformat(),
    }
    try:
        save_expenses([*expenses, expense], file_path)
    except OSError as error:
        print(f"Could not save expense: {error}")
        return

    expenses.append(expense)
    print("Expense added.")


def show_expenses(expenses: list[dict[str, str]]) -> None:
    if not expenses:
        print("No expenses recorded yet.")
        return

    print("\nYour expenses:")
    for number, expense in enumerate(expenses, start=1):
        print(
            f"{number}. {expense['date']} - {expense['description']}: "
            f"${Decimal(expense['amount']):.2f}"
        )


def show_total(expenses: list[dict[str, str]]) -> None:
    total = sum((Decimal(expense["amount"]) for expense in expenses), Decimal("0"))
    print(f"Total expenses: ${total:.2f}")


def main() -> None:
    try:
        expenses = load_expenses()
    except (OSError, ValueError) as error:
        print(f"Could not load expenses: {error}")
        return

    while True:
        print("\nExpense Tracker")
        print("1. Add an expense")
        print("2. View expenses")
        print("3. View total")
        print("4. Exit")

        choice = input("Choose an option: ").strip()
        if choice == "1":
            add_expense(expenses)
        elif choice == "2":
            show_expenses(expenses)
        elif choice == "3":
            show_total(expenses)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Please choose 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
