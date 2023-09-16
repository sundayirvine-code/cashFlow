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

def calculate_income_totals_formatted_debt(user_id, start_date=None, end_date=None):
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
    from models import Credit

    # If start_date is not provided, set it to the beginning of the current month
    if not start_date:
        today = date.today()
        start_date = date(today.year, today.month, 1)

    # If end_date is not provided, set it to the current date
    if not end_date:
        end_date = date.today()

    income_totals = calculate_income_totals(user_id, start_date, end_date)

    # Query unique debtor names for the current user
    debtor_names = (
        db.session.query(Credit.debtor)
        .filter_by(user_id=user_id)
        .distinct()
        .all()
    )

    # Extract the debtor names from the query result
    unique_debtors = [debtor[0] for debtor in debtor_names]
    '''
    COME BACK HERE WHEN DEALING WITH DEBT
    '''
    # Calculate the sum of amount_payed for each debtor
    debtor_totals = {}
    for debtor_name in unique_debtors:
        total_amount_payed = (
            db.session.query(db.func.sum(Credit.amount_payed))
            .filter_by(user_id=user_id, debtor=debtor_name)
            .scalar()
        )
        if total_amount_payed is None:
            total_amount_payed = 0
        debtor_totals[debtor_name] = total_amount_payed

    # Calculate the sum of all amount_payed values in the debtor_totals dictionary
    total_debt_amount = sum(debtor_totals.values())

    # Add the total_debt_amount to the income_totals dictionary with 'Debt' as the key
    income_totals['Debt'] = total_debt_amount
  

    # Calculate the total income
    total_income = sum(income_totals.values())

    # Initialize a dictionary to store formatted amounts and percentages
    formatted_income_totals = {}

    # Format the amount values and update the income_totals dictionary
    for category, amount in income_totals.items():
        formatted_amount = "{:,.2f}/=".format(amount)
        try:
            percentage = "{:.2f}".format((amount / total_income) * 100)
        except ZeroDivisionError:
            percentage = "{:.2f}".format(0)
        formatted_income_totals[category] = (formatted_amount, percentage)

    # Replace the original income_totals dictionary with the formatted one
    income_totals = formatted_income_totals

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

    '''# Get the current month's budget for the user
    today = datetime.today()
    current_year = today.year
    current_month = today.month'''

    
    
    # Get the current month's budget for the user
    budget = Budget.query.filter_by(user_id=cashout.user_id, year=cashout.date.year, month=cashout.date.month).first()

    print('testing budget found', budget)
    if not budget:
        return "No Budget exists for that transaction."

    # Check if the associated expense is part of the budget
    budget_expense = BudgetExpense.query.filter_by(budget_id=budget.id, expense_id=expense.id).first()

    if not budget_expense:
        return "Associated expense is not part of the budget"

    # Update the spent_amount of the BudgetExpense
    budget_expense.update_spent_amount(cashout.amount) 

    try:
        db.session.commit()
        return budget_expense.spent_amount
    except Exception as e:
        db.session.rollback()
        return str(e)

def create_debt(user_id, creditor, amount, date, description=None, date_due=None):
    """
    Create a debt transaction for a user.

    Args:
        user_id (int): The ID of the user.
        creditor (str): The name of the creditor (will be converted to title case).
        amount (float): The amount of the debt.
        date (date): The date of the debt transaction.
        description (str, optional): A description of the debt.
        date_due (date, optional): The date when the debt is due to be paid.

    Returns:
        Union[Debt, str]: The created Debt instance or an error message.
    """
    from models import Debt

    # Convert creditor to title case
    creditor = creditor.title()

    # Check if debt with same user_id and creditor already exists
    existing_debt = Debt.query.filter_by(user_id=user_id, creditor=creditor).first()
    if existing_debt:
        return "Debt with the same creditor already exists for this user."

    # Create and add the Debt instance
    debt = Debt(user_id=user_id, creditor=creditor, amount=amount, date=date,
                description=description, date_due=date_due)
    
    try:
        db.session.add(debt)
        db.session.commit()
        return debt
    except Exception as e:
        db.session.rollback()
        return str(e)

def create_credit(user_id, debtor, amount, date, description=None, date_due=None):
    """
    Create a credit transaction for a user.

    Args:
        user_id (int): The ID of the user.
        debtor (str): The name of the debtor 
        amount (float): The amount of the credit.
        date (date): The date of the credit transaction.
        description (str, optional): A description of the credit.
        date_due (date, optional): The date when the credit is due to be received.

    Returns:
        Union[Credit, str]: The created Credit instance or an error message.
    """
    from models import Credit

    # Convert debtor to title case
    debtor = debtor.title()

    # Check if credit with same user_id and debtor already exists
    existing_credit = Credit.query.filter_by(user_id=user_id, debtor=debtor).first()
    if existing_credit:
        return "Credit with the same debtor already exists for this user."

    # Create and add the Credit instance
    credit = Credit(user_id=user_id, debtor=debtor, amount=amount, date=date,
                    description=description, date_due=date_due)
    try:
        db.session.add(credit)
        db.session.commit()
        return credit
    except Exception as e:
        db.session.rollback()
        return str(e)

def add_cash_out_transaction(user_id, amount, date, expense_id, description=None, settled_debt_id=None):
    """
    Add a CashOut transaction to the database.

    Args:
        user_id (int): The user's ID associated with the transaction.
        amount (float): The amount of the cash outflow.
        date (date): The date of the transaction.
        expense_id (int): The ID of the associated expense.
        description (str, optional): A description of the transaction.
        settled_debt_id (int, optional): The ID of the associated Debt instance for debt settlement.

    Returns:
        CashOut: The created CashOut transaction instance.

    Raises:
        ValueError: If expense_id corresponds to an existing Expense with user_id 0 but settled_debt is not provided.
        ValueError: If the debt is already paid.
        ValueError: If the paid amount exceeds the debt amount.
    """
    from models import Expense, CashOut, Debt

    if expense_id:
        expense = Expense.query.get(expense_id)
        if expense and expense.user_id == 0:
            if not settled_debt_id:
                raise ValueError("For debt payment transactions, settled_debt must be provided.")

            # Query the debt being paid by its ID
            debt_to_pay = Debt.query.get(settled_debt_id)
            if not debt_to_pay:
                raise ValueError("Invalid debt ID provided for settlement.")

            if debt_to_pay.is_paid:
                raise ValueError("The debt is already paid.")

            if debt_to_pay.amount_payed + amount > debt_to_pay.amount:
                raise ValueError("Paid amount exceeds the debt amount.")

            # Add cash out with all fields populated
            cash_out = CashOut(
                user_id=user_id,
                amount=amount,
                date=date,
                expense_id=expense_id,
                description=description,
                settled_debt_id=settled_debt_id)

            try:
                db.session.add(cash_out)
                db.session.commit()

                # Update the debt being paid by this transaction
                debt_to_pay.amount_payed += amount

                # If paid amount equals or exceeds debt amount, mark the debt as paid
                if debt_to_pay.amount_payed >= debt_to_pay.amount:
                    debt_to_pay.is_paid = True

                db.session.commit()

            except Exception as e:
                db.session.rollback()
                return str(e)

            return cash_out

    cash_out = CashOut(
        user_id=user_id,
        amount=amount,
        date=date,
        expense_id=expense_id,
        description=description,
        settled_debt_id=None
    )

    try:
        db.session.add(cash_out)
        db.session.commit()
        return cash_out
    except Exception as e:
        db.session.rollback()
        return str(e)

def add_cash_in_transaction(user_id, amount, date, income_id, description=None, settled_credit_id=None):
    """
    Add a CashIn transaction to the database.

    Args:
        user_id (int): The user's ID associated with the transaction.
        amount (float): The amount of the cash inflow.
        date (date): The date of the transaction.
        income_id (int): The ID of the associated income.
        description (str, optional): A description of the transaction.
        settled_credit_id (int, optional): The ID of the associated Credit instance for credit settlement.

    Returns:
        CashIn: The created CashIn transaction instance.

    Raises:
        ValueError: If income_id corresponds to an existing Income with user_id 0 but settled_credit is not provided.
        ValueError: If the credit is already settled.
        ValueError: If the received amount exceeds the credit amount.
    """
    from models import Income, CashIn, Credit

    if income_id:
        income = Income.query.get(income_id)
        if income and income.user_id == 0:
            if not settled_credit_id:
                raise ValueError("For credit settlement transactions, settled_credit_id must be provided.")

            # Query the credit being settled by its ID
            credit_to_settle = Credit.query.get(settled_credit_id)
            if not credit_to_settle:
                raise ValueError("Invalid credit ID provided for settlement.")

            if credit_to_settle.is_paid:
                raise ValueError("The credit is already settled.")

            if credit_to_settle.amount_payed + amount > credit_to_settle.amount:
                raise ValueError("Received amount exceeds the credit amount.")

            # Add cash in with all fields populated
            cash_in = CashIn(
                user_id=user_id,
                amount=amount,
                date=date,
                income_id=income_id,
                description=description,
                settled_credit_id=settled_credit_id
            )

            try:
                db.session.add(cash_in)
                db.session.commit()

                # Update the credit being settled by this transaction
                credit_to_settle.amount_payed += amount

                # If received amount equals or exceeds credit amount, mark the credit as settled
                if credit_to_settle.amount_payed >= credit_to_settle.amount:
                    credit_to_settle.is_paid = True

                db.session.commit()

            except Exception as e:
                db.session.rollback()
                return str(e)

            return cash_in

    cash_in = CashIn(
        user_id=user_id,
        amount=amount,
        date=date,
        income_id=income_id,
        description=description,
        settled_credit_id=None
    )

    try:
        db.session.add(cash_in)
        db.session.commit()
        return cash_in
    except Exception as e:
        db.session.rollback()
        return str(e)
