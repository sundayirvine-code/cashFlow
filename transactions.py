from models import db
from datetime import datetime

def add_income(user_id, income_name, income_type_id):
    """
    Add an income category for a user.

    Args:
        user_id (int): The user's ID.
        income_name (str): The name of the income transaction.
        income_type_id (int): The ID of the associated income type.

    Returns:
        bool/str: True if addition is successful, otherwise an error message.

    """
    from models import Income

    # Convert income_name to title case and remove leading/trailing whitespace
    income_name = income_name.strip().title()

    if income_name == '':
        return "Empty strings are not allowed"

    # Check if the income already exists
    existing_income = Income.query.filter_by(user_id=user_id, name=income_name).first()
    if existing_income:
        return "Income transaction already exists."
    
    # Create a new income transaction instance
    income = Income(user_id=user_id, name=income_name, income_type_id=income_type_id)

    try:
        db.session.add(income)
        db.session.commit()
        return True, income
    except Exception as e:
        db.session.rollback()
        return str(e)

def calculate_income_totals(user_id, start_date=None, end_date=None):
    """
    Calculate the total income amounts for each income category of a user within a specified date range.

    Args:
        user_id (int): The user's ID for whom income totals are calculated.
        start_date (date, optional): The start date of the date range (inclusive). If not provided, it defaults to the
            beginning of the current month.
        end_date (date, optional): The end date of the date range (inclusive). If not provided, it defaults to the
            current date.

    Returns:
        dict: A dictionary where keys are income category names (str) and values are the corresponding total amounts (float).

    Example:
        # Calculate income totals for the current user for the current month
        user_id = current_user.id
        income_totals = calculate_income_totals(user_id)
        print(income_totals)
        
        # Calculate income totals for the current user for a custom date range
        start_date = date(2023, 1, 1)
        end_date = date(2023, 1, 31)
        income_totals = calculate_income_totals(user_id, start_date, end_date)
        print(income_totals)
    """
    from datetime import date
    from models import Income, CashIn

    # If start_date is not provided, set it to the beginning of the current month
    if not start_date:
        today = date.today()
        start_date = date(today.year, today.month, 1)

    # If end_date is not provided, set it to the current date
    if not end_date:
        end_date = date.today()

    # Query all income categories for the user
    income_categories = Income.query.filter_by(user_id=user_id).all()

    # Initialize a dictionary to store income category names and their corresponding total amounts
    income_totals = {}

    # Iterate through each income category
    for category in income_categories:
        # Query CashIn transactions for the specific income category within the date range
        total_amount = CashIn.query.filter(
            CashIn.user_id == user_id,
            CashIn.income_id == category.id,
            CashIn.date >= start_date,
            CashIn.date <= end_date
        ).with_entities(db.func.sum(CashIn.amount)).scalar()

        # If there are no transactions, set total_amount to 0
        if total_amount is None:
            total_amount = 0

        # Add the income category name and total amount to the income_totals dictionary
        income_totals[category.name] = total_amount

    return income_totals

def calculate_expense_totals(user_id, start_date=None, end_date=None):
    """
    Calculate the total expense amounts for each expense category of a user within a specified date range.

    Args:
        user_id (int): The user's ID for whom expense totals are calculated.
        start_date (date, optional): The start date of the date range (inclusive). If not provided, it defaults to the
            beginning of the current month.
        end_date (date, optional): The end date of the date range (inclusive). If not provided, it defaults to the
            current date.

    Returns:
        list: A list of dictionaries, where each dictionary contains 'name', 'amount', and 'percentage' keys.

    Example:
        # Calculate expense totals for the current user for the current month
        user_id = current_user.id
        expense_totals = calculate_expense_totals(user_id)
        print(expense_totals)
        
        # Calculate expense totals for the current user for a custom date range
        start_date = date(2023, 1, 1)
        end_date = date(2023, 1, 31)
        expense_totals = calculate_expense_totals(user_id, start_date, end_date)
        print(expense_totals)
    """
    from datetime import date
    from models import Expense, CashOut
    
    # If start_date is not provided, set it to the beginning of the current month
    if not start_date:
        today = date.today()
        start_date = date(today.year, today.month, 1)

    # If end_date is not provided, set it to the current date
    if not end_date:
        end_date = date.today()

    # Query all expense categories for the user
    expense_categories = Expense.query.filter_by(user_id=user_id).all()

    # Initialize a list to store expense category totals
    expense_totals = {}

    # Iterate through each expense category
    for category in expense_categories:
        # Query CashOut transactions for the specific expense category within the date range
        total_amount = CashOut.query.filter(
            CashOut.user_id == user_id,
            CashOut.expense_id == category.id,
            CashOut.date >= start_date,
            CashOut.date <= end_date
        ).with_entities(db.func.sum(CashOut.amount)).scalar()

        # If there are no transactions, set total_amount to 0
        if total_amount is None:
            total_amount = 0

        # Add the income category name and total amount to the income_totals dictionary
        expense_totals[category.name] = total_amount

    return expense_totals

