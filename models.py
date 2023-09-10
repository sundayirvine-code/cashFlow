from flask_sqlalchemy import SQLAlchemy
from decimal import Decimal
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    """
    Represents a user of the application.

    Attributes:
        id (int): The unique identifier for the user.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        password (str): The password associated with the user.
        email (str): The email address of the user (unique).
    Methods:
        __repr__: Returns a string representation of the User object.
    """

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"<User {self.id}: {self.first_name} {self.last_name}>"

class IncomeType(db.Model):
    """
    Represents different types of income sources.

    Attributes:
        id (int): The unique identifier for the income type.
        name (str): The name of the income type.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<IncomeType {self.name}>"

class Income(db.Model):
    """
    Represents an income category associated with a user and an income type.

    Attributes:
        id (int): The unique identifier for the income transaction.
        name (str): The name of the income.
        user_id (int): The foreign key referencing the associated User.
        income_type_id (int): The foreign key referencing the associated IncomeType.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    income_type_id = db.Column(db.Integer, db.ForeignKey('income_type.id'), nullable=False)

    def __repr__(self):
        return f"<Income {self.name}>"

class Expense(db.Model):
    """
    Represents an expense category associated with a user.

    Attributes:
        id (int): The unique identifier for the expense transaction.
        name (str): The name of the expense.
        user_id (int): The foreign key referencing the associated User.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    budget_expenses = db.relationship('BudgetExpense', back_populates='expense', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Expense {self.name}>"

class CashIn(db.Model):
    """
    Represents a cash inflow transaction associated with a user and an income.

    Attributes:
        id (int): The unique identifier for the cash inflow transaction.
        user_id (int): The foreign key referencing the associated User.
        income_id (int): The foreign key referencing the associated Income.
        amount (float): The amount of cash inflow.
        date (date): The date of the cash inflow transaction.
        description: Details of the transaction
        settled_credit_id (int): The foreign key referencing the associated Credit (optional).
        settled_credit (relationship): Many-to-one relationship with Credit.
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    income_id = db.Column(db.Integer, db.ForeignKey('income.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(100), nullable=True)
    settled_credit_id = db.Column(db.Integer, db.ForeignKey('credit.id'), nullable=True)

    settled_credit = db.relationship('Credit', back_populates='cash_in_transactions')

    def update_transaction(self, new_description, new_amount, new_date):
        # Update the transaction attributes
        self.description = new_description
        self.amount = new_amount
        self.date = new_date
        db.session.commit()

    def delete_transaction(self):
        # Delete the transaction from the database
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f"<CashIn {self.amount} on {self.date}>"

class CashOut(db.Model):
    """
    Represents a cash outflow transaction associated with a user and an expense.

    Attributes:
        id (int): The unique identifier for the cash outflow transaction.
        user_id (int): The foreign key referencing the associated User.
        amount (float): The amount of cash outflow.
        date (date): The date of the cash outflow transaction.
        expense_id (int): The foreign key referencing the associated Expense.
        description: Details of the transaction
        settled_debt_id (int): The foreign key referencing the associated Debt (optional).
        settled_debt (relationship): Many-to-one relationship with Debt.
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, nullable=False)
    expense_id = db.Column(db.Integer, db.ForeignKey('expense.id'), nullable=False)
    description = db.Column(db.String(100), nullable=True)
    settled_debt_id = db.Column(db.Integer, db.ForeignKey('debt.id'), nullable=True)

    settled_debt = db.relationship('Debt', back_populates='cash_out_transactions')

    def update_transaction(self, new_description, new_amount, new_date):
        # Update the transaction attributes
        self.description = new_description
        self.amount = new_amount
        self.date = new_date
        db.session.commit()

    def delete_transaction(self):
        # Delete the transaction from the database
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f"<CashOut {self.amount} on {self.date}>"


