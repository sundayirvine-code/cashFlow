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

def add_expense(user_id, expense_name):
    """
    Add an expense category for a user.

    Args:
        user_id (int): The user's ID.
        expense_name (str): The name of the expense transaction.

    Returns:
        bool/str: True if addition is successful, otherwise an error message.

    """
    from models import Expense

    # Convert expense_name to title case and remove leading/trailing whitespace
    expense_name = expense_name.strip().title()
    
    # Check if the expense already exists
    existing_expense = Expense.query.filter_by(user_id=user_id, name=expense_name).first()
    if existing_expense:
        return "Expense transaction already exists."
    
    # Create a new expense transaction instance
    expense = Expense(user_id=user_id, name=expense_name)

    try:
        db.session.add(expense)
        db.session.commit()
        return expense
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

def create_budget(user_id, year, month):
    """
    Create a budget for a specific user, year, and month.

    Args:
        user_id (int): The user's ID.
        year (int): The year of the budget.
        month (int): The month of the budget.

    Returns:
        Budget or str: The created Budget instance if successful, or an error message if unsuccessful.
    """
    from models import Budget

    existing_budget = Budget.query.filter_by(user_id=user_id, year=year, month=month).first()
    if existing_budget:
        return "A budget already exists for this month."

    budget = Budget(user_id=user_id, year=year, month=month)

    try:
        db.session.add(budget)
        db.session.commit()
        return budget
    except Exception as e:
        db.session.rollback()
        return str(e)

def add_budget_expense(budget_id, expense_id, expected_amount):
    """
    Add an expense to a budget with the expected amount.

    Args:
        budget_id (int): The ID of the budget.
        expense_id (int): The ID of the associated expense.
        expected_amount (float): The expected amount to be spent on the expense.

    Returns:
        BudgetExpense or str: The created BudgetExpense instance if successful, or an error message if unsuccessful.
    """
    from models import BudgetExpense

    existing_budget_expense = BudgetExpense.query.filter_by(budget_id=budget_id, expense_id=expense_id).first()
    if existing_budget_expense:
        return "An expense with the same ID already exists in this budget."
    
    budget_expense = BudgetExpense(budget_id=budget_id, expense_id=expense_id, expected_amount=expected_amount)

    try:
        db.session.add(budget_expense)
        db.session.commit()
        return budget_expense
    except Exception as e:
        db.session.rollback()
        return str(e)

def update_budget_expense_with_cashout(cashout_id):
    """
    Update BudgetExpense with the amount of a CashOut transaction.

    Args:
        cashout_id (int): The ID of the CashOut transaction to be processed.
    Returns:
        float or str: The new spent_amount of the BudgetExpense if successful, or an error message if unsuccessful.
    """
    from models import CashOut, Expense, Budget, BudgetExpense

    cashout = db.session.get(CashOut, cashout_id)

    if not cashout:
        return "CashOut transaction not found."

    # Get the associated expense
    expense = db.session.get(Expense, cashout.expense_id)

    if not expense:
        return "Associated expense not found."

    # Get the current month's budget for the user
    today = datetime.today()
    current_year = today.year
    current_month = today.month

    if cashout.date.year != current_year or cashout.date.month != current_month:
        # try to get the associated budget when this is returned.
        return "CashOut transaction is not in the current Budget's year and month."
    
    # Get the current month's budget for the user
    budget = Budget.query.filter_by(user_id=cashout.user_id, year=current_year, month=current_month).first()

    if not budget:
        return "Budget for the current month not found."

    # Check if the associated expense is part of the budget
    budget_expense = BudgetExpense.query.filter_by(budget_id=budget.id, expense_id=expense.id).first()

    if not budget_expense:
        return "Associated expense is not part of the budget for the current month."

    # Update the spent_amount of the BudgetExpense
    budget_expense.spent_amount += cashout.amount

    try:
        db.session.commit()
        return budget_expense.spent_amount
    except Exception as e:
        db.session.rollback()
        return str(e)
