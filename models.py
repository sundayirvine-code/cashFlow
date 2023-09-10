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

