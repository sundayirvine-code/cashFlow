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
