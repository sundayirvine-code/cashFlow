# tests/test_transactions.py

import unittest
from app import app, db
from transactions import add_income, add_expense, create_budget, add_budget_expense, update_budget_expense_with_cashout
from models import User, IncomeType, Income, Expense, Budget, BudgetExpense, CashOut
from datetime import datetime

class TestTransactions(unittest.TestCase):

    def setUp(self):
        """
        Set up the test environment.
        
        This method configures the Flask app for testing, creates a separate
        in-memory SQLite database, and prepares a test client for making requests.
        """
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # Use a separate test database
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """
        Clean up the test environment.
        
        This method removes the test database and resets the app context after each test.
        """
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_income(self):
        """
        Test adding an income transaction.

        This test creates a user, an income type, and then adds an income transaction for the user.
        It checks if the income transaction was added correctly to the database.

        """
        with app.app_context():
            # Add a user and an income type
            user = User(first_name='test_user', last_name='test_user', password='test_password', email='test@example.com')
            db.session.add(user)
            db.session.commit()
            income_type = IncomeType(name="Salary")
            db.session.add(income_type)
            db.session.commit()

            # Add an income transaction
            result = add_income(user.id, "Monthly Salary", income_type.id)
            self.assertTrue(result)

            # Check if the income transaction was added
            income = Income.query.first()
            self.assertIsNotNone(income)
            self.assertEqual(income.name, "Monthly Salary")
            self.assertEqual(income.income_type_id, income_type.id)

    def test_add_expense(self):
        """
        Test adding an expense transaction.

        This test creates a user and then adds an expense transaction for the user.
        It checks if the expense transaction was added correctly to the database.

        """
        with app.app_context():
        # Add a user
            user = User(first_name='test_user', last_name='test_user', password='test_password', email='test@example.com')
            db.session.add(user)
            db.session.commit()

            # Add an expense transaction
            result = add_expense(user.id, "Groceries")
            self.assertTrue(result)

            # Check if the expense transaction was added
            expense = Expense.query.first()
            self.assertIsNotNone(expense)
        self.assertEqual(expense.name, "Groceries")

    def test_create_budget(self):
        """
        Test creating a budget for a user.
        """
        with app.app_context():
            # Add a user
            user = User(first_name='test_user', last_name='test_user', password='test_password', email='test@example.com')
            db.session.add(user)
            db.session.commit()

            # Create a budget for the user
            result = create_budget(user.id, 2023, 8)
            self.assertIsInstance(result, Budget)

            # Check if the budget was created
            budget = Budget.query.first()
            self.assertIsNotNone(budget)
            self.assertEqual(budget.user_id, user.id)
            self.assertEqual(budget.year, 2023)
            self.assertEqual(budget.month, 8)

            # Attempt to create a duplicate budget for the same month
            result_duplicate = create_budget(user.id, 2023, 8)
            self.assertEqual(result_duplicate, "A budget already exists for this month.")

    def test_add_budget_expense(self):
        """
        Test adding an expense to a budget.
        """
        with app.app_context():
            # Add a user and an expense
            user = User(first_name='test_user', last_name='test_user', password='test_password', email='test@example.com')
            db.session.add(user)
            db.session.commit()
            expense = Expense(user_id=user.id, name="Groceries")
            db.session.add(expense)
            db.session.commit()

            # Create a budget
            budget = Budget(user_id=user.id, year=2023, month=8)
            db.session.add(budget)
            db.session.commit()

            # Add a budget expense
            result = add_budget_expense(budget.id, expense.id, 500.00)
            self.assertIsInstance(result, BudgetExpense)

            # Check if the budget expense was added
            budget_expense = BudgetExpense.query.first()
            self.assertIsNotNone(budget_expense)
            self.assertEqual(budget_expense.budget_id, budget.id)
            self.assertEqual(budget_expense.expense_id, expense.id)
            self.assertEqual(budget_expense.expected_amount, 500.00)

           # Attempt to add a duplicate budget expense
            result_duplicate = add_budget_expense(budget.id, expense.id, 600.00)
            self.assertEqual(result_duplicate, "An expense with the same ID already exists in this budget.")

            # Check that only one budget expense was added
            budget_expenses = BudgetExpense.query.all()
            self.assertEqual(len(budget_expenses), 1)

    
    def test_update_budget_expense_with_cashout(self):
        """
        Test updating a budget expense with a CashOut transaction.

        This function tests various scenarios:
        - Invalid CashOut ID
        - Invalid Expense ID
        - Invalid Budget for Current Month
        - Expense Not Part of Current Month's Budget
        - Updated Budget Expense

        """
        with app.app_context():
            # Add a user
            user = User(first_name='test_user', last_name='test_user', password='test_password', email='test@example.com')
            db.session.add(user)
            db.session.commit()

            # Add expenses
            expense = Expense(user_id=user.id, name="Groceries")
            expense2 = Expense(user_id=user.id, name="Utilities")
            db.session.add_all([expense, expense2])
            db.session.commit()

            today = datetime.today()
            current_year = today.year
            current_month = today.month

            # Add a CashOut transaction with the current month and year
            cashout1 = CashOut(user_id=user.id, amount=45.00, date=today, expense_id=expense.id)
            db.session.add(cashout1)
            db.session.commit()

            # Update the budget expense with the CashOut amount
            result = update_budget_expense_with_cashout(cashout1.id)

            # Check if the result matches the expected error message
            self.assertEqual(result, "Budget for the current month not found.")

            # Add a budget for the current month
            budget = Budget(user_id=user.id, year=current_year, month=current_month)
            db.session.add(budget)
            db.session.commit()


            # Add a budget expense for the expense in the budget
            budget_expense = BudgetExpense(budget_id=budget.id, expense_id=expense.id, expected_amount=100.00)
            db.session.add(budget_expense)
            db.session.commit()

            # Add a CashOut transaction
            cashout = CashOut(user_id=user.id, amount=50.00, date=today, expense_id=expense.id)
            db.session.add(cashout)
            db.session.commit()

             # Test 1: Invalid CashOut ID
            invalid_cashout_id = 9999
            result_invalid_cashout_id = update_budget_expense_with_cashout(invalid_cashout_id)
            self.assertEqual(result_invalid_cashout_id, "CashOut transaction not found.")

            # Test 2: Invalid Expense ID
            invalid_expense_id = 9999
            cashout_with_invalid_expense = CashOut(user_id=user.id, amount=50.00, date=today, expense_id=invalid_expense_id)
            db.session.add(cashout_with_invalid_expense)
            db.session.commit()
            result_invalid_expense_id = update_budget_expense_with_cashout(cashout_with_invalid_expense.id)
            self.assertEqual(result_invalid_expense_id,
            "Associated expense not found.")

            # Test 3: Invalid Budget for Current Month
            cashout_invalid_month = CashOut(user_id=user.id, amount=50.00, date=datetime(2023, 12, 15), expense_id=expense.id)
            db.session.add(cashout_invalid_month)
            db.session.commit()
            result_invalid_month = update_budget_expense_with_cashout(cashout_invalid_month.id)
            self.assertEqual(result_invalid_month, "CashOut transaction is not in the current Budget's year and month.")

            # Test 4: Expense Not Part of Current Month's Budget
            other_expense = Expense(user_id=user.id, name="Other Expense")
            db.session.add(other_expense)
            db.session.commit()
            cashout_other_expense = CashOut(user_id=user.id, amount=30.00, date=today, expense_id=other_expense.id)
            db.session.add(cashout_other_expense)
            db.session.commit()
            result_expense_not_in_budget = update_budget_expense_with_cashout(cashout_other_expense.id)
            self.assertEqual(result_expense_not_in_budget, "Associated expense is not part of the budget for the current month.")

            # Test 5: Updated Budget Expense
            updated_spent_amount = update_budget_expense_with_cashout(cashout.id)
            updated_budget_expense = db.session.get(BudgetExpense, budget_expense.id)
            self.assertEqual(updated_spent_amount, updated_budget_expense.spent_amount)

            # Update the budget expense with the CashOut amount
            updated_spent_amount = update_budget_expense_with_cashout(cashout.id)

            # Get the updated budget expense from the session
            updated_budget_expense = db.session.get(BudgetExpense, budget_expense.id)

            # Check if the budget expense's spent_amount was updated correctly
            self.assertEqual(updated_spent_amount, updated_budget_expense.spent_amount)

    def test_update_budget_expense_with_cashout_multiple_expenses(self):
        """
        Test updating multiple budget expenses with CashOut transactions.

        This function tests the case where there are multiple BudgetExpense entries for different expenses within the same budget.

        """
        with app.app_context():
            # Add a user
            user = User(first_name='test_user', last_name='test_user', password='test_password', email='test@example.com')
            db.session.add(user)
            db.session.commit()

            # Add expenses
            expense = Expense(user_id=user.id, name="Groceries")
            other_expense = Expense(user_id=user.id, name="Utilities")
            db.session.add_all([expense, other_expense])
            db.session.commit()

            # Add a budget for the current month
            today = datetime.today()
            current_year = today.year
            current_month = today.month
            budget = Budget(user_id=user.id, year=current_year, month=current_month)
            db.session.add(budget)
            db.session.commit()

            # Add budget expenses for different expenses in the budget
            budget_expense_other_expense = BudgetExpense(budget_id=budget.id, expense_id=other_expense.id, expected_amount=50.00)
            budget_expense = BudgetExpense(budget_id=budget.id, expense_id=expense.id, expected_amount=100.00)
            db.session.add_all([budget_expense_other_expense, budget_expense])
            db.session.commit()

            # Add CashOut transactions for both expenses
            cashout_expense = CashOut(user_id=user.id, amount=30.00, date=today, expense_id=expense.id)
            cashout_other_expense = CashOut(user_id=user.id, amount=20.00, date=today, expense_id=other_expense.id)
            db.session.add_all([cashout_expense, cashout_other_expense])
            db.session.commit()

            # Update the budget expenses with the CashOut amounts
            result_expense = update_budget_expense_with_cashout(cashout_expense.id)
            result_other_expense = update_budget_expense_with_cashout(cashout_other_expense.id)

            # Get the updated budget expenses from the session
            updated_budget_expense = db.session.get(BudgetExpense, budget_expense.id)
            updated_budget_expense_other_expense = db.session.get(BudgetExpense, budget_expense_other_expense.id)

            # Calculate the expected results
            expected_result_expense = budget_expense.spent_amount 
            expected_result_other_expense = budget_expense_other_expense.spent_amount 

            # Check if the budget expenses' spent_amounts were updated correctly
            self.assertEqual(result_expense, expected_result_expense)
            self.assertEqual(result_other_expense, expected_result_other_expense)
            self.assertEqual(updated_budget_expense.spent_amount, expected_result_expense)
            self.assertEqual(updated_budget_expense_other_expense.spent_amount, expected_result_other_expense)

    def test_update_budget_expense_with_multiple_cashouts(self):
        """
        Test updating a budget expense with multiple CashOut transactions for the same expense.

        This function ensures that the function correctly accumulates the spent amount from all CashOut transactions.

        """
        with app.app_context():
            # Add a user
            user = User(first_name='test_user', last_name='test_user', password='test_password', email='test@example.com')
            db.session.add(user)
            db.session.commit()

            # Add an expense
            expense = Expense(user_id=user.id, name="Groceries")
            db.session.add(expense)
            db.session.commit()

            # Add a budget for the current month
            today = datetime.today()
            current_year = today.year
            current_month = today.month
            budget = Budget(user_id=user.id, year=current_year, month=current_month)
            db.session.add(budget)
            db.session.commit()

            # Add a budget expense for the expense in the budget
            budget_expense = BudgetExpense(budget_id=budget.id, expense_id=expense.id, expected_amount=100.00)
            db.session.add(budget_expense)
            db.session.commit()

            # Add multiple CashOut transactions for the same expense
            cashout1 = CashOut(user_id=user.id, amount=30.00, date=today, expense_id=expense.id)
            cashout2 = CashOut(user_id=user.id, amount=50.00, date=today, expense_id=expense.id)
            cashout3 = CashOut(user_id=user.id, amount=20.00, date=today, expense_id=expense.id)
            db.session.add_all([cashout1, cashout2, cashout3])
            db.session.commit()

            # Update the budget expense with the CashOut amounts
            updated_spent_amount = update_budget_expense_with_cashout(cashout1.id)
            updated_spent_amount = update_budget_expense_with_cashout(cashout2.id)
            updated_spent_amount = update_budget_expense_with_cashout(cashout3.id)

            # Get the updated budget expense from the session
            updated_budget_expense = db.session.get(BudgetExpense, budget_expense.id)

            # Calculate the expected total spent amount from CashOut transactions
            expected_total_spent_amount = cashout1.amount + cashout2.amount + cashout3.amount

            # Check if the budget expense's spent_amount was updated correctly
            self.assertEqual(updated_spent_amount, expected_total_spent_amount)
            self.assertEqual(updated_budget_expense.spent_amount, expected_total_spent_amount)


if __name__ == "__main__":
    unittest.main()
