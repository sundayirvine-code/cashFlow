from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, abort
from auth import register_user, authenticate_user
from forms import RegistrationForm, LoginForm, IncomeCategoryForm, IncomeTransactionForm
from models import db, initialize_default_income_types, User, Income, IncomeType, Credit, CashIn, Expense, Debt, CashOut, Budget, BudgetExpense, DebtorPayment, CreditorPayment
from flask_login import login_required, logout_user, LoginManager, login_user, current_user
from transactions import add_income, add_cash_in_transaction, calculate_income_totals, add_expense, calculate_expense_totals, add_cash_out_transaction, calculate_income_totals_formatted_debt, create_budget
from datetime import date, datetime, timedelta
from calculations import calculate_total_income_between_dates, calculate_total_expenses_between_dates, calculate_expense_percentage_of_income
from sqlalchemy import func
from titlecase import titlecase
from decimal import Decimal
import os
from dotenv import load_dotenv
import pymysql
from flask_migrate import Migrate

# Load environment variables from .env file
load_dotenv()

pymysql.install_as_MySQLdb()


# Configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
#app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

migrate = Migrate(app, db, render_as_batch=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Home Page(landing page)
@app.route('/')
def home():
    """
    Render the home page.

    Returns:
        str: The rendered HTML template for the home page.
    """
    return render_template('home.html')

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle the login page.

    If the user is already authenticated, redirect to the dashboard page.
    If the request method is GET, render the login form.
    If the request method is POST, process the form data and authenticate the user.

    Returns:
        str: The rendered HTML template for the login page, with the login form or flash messages.
    """
    
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = authenticate_user(email, password)
        if user:
            login_user(user)
            if current_user.is_authenticated:
                username = current_user.first_name
            return redirect(url_for('dashboard', username=username))  
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html', form=form)

# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle the Register page.

    If the request method is GET, render the signup form.
    If the request method is POST, process the form data and create a new user.

    Returns:
        str: The rendered HTML template for the register page, with the register form or flash messages.
    """
    form = RegistrationForm()

    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        password = form.password.data
        email = form.email.data

        # Check if the email already exists in the database
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        # Create a new user
        new_user = register_user(first_name=first_name, last_name=last_name, password=password, email=email)

        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# User logout
@app.route('/logout')
@login_required
def logout():
    """
    Log out the current user.

    Returns:
        redirect: Redirects the user to the home page.
    """
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))

@app.route('/chart_data', methods=['POST'])
def chart_data():
    # Expense Chart
    expense_percentages = calculate_expense_percentage_of_income(current_user.id)

    # Sort the expenses by percentage in descending order
    expense_percentages.sort(key=lambda x: x['percentage'], reverse=True)

    # Extract the top 6 expenses and their percentages
    top_expenses = expense_percentages[:6]

    # Calculate the total percentage of the remaining expenses
    remaining_percentage = sum(expense['percentage'] for expense in expense_percentages[6:])

    # Create labels and values for the chart
    labels = [expense['expense_name'] for expense in top_expenses] + ['Others']
    values = [expense['percentage'] for expense in top_expenses] + [remaining_percentage]

    colors = ['#ffb65d', '#465bca', '#9d3171', '#3eeed0', '#ff5497', '#309a6a', '#141c33']
    expense_chart_data = {
        'labels': labels,
        'values': values,
        'colors': colors,
    }

    # Income chart
    # Query the contribution of each category to the user's total income
    income_totals = calculate_income_totals(current_user.id)

    today = date.today()
    start_date = date(today.year, today.month, 1)
    end_date = date.today()

    # Sum the amount for the current user's credits settled since the beginning of the month
    total_amount_paid = db.session.query(func.sum(CashIn.amount)).filter(
        CashIn.income_id==2,
        CashIn.user_id == current_user.id,
        CashIn.date >= start_date,
        CashIn.date <= end_date
    ).scalar()

    if total_amount_paid is None:
        total_amount_paid = 0 

    # Sum the debt taken the beginning of the month
    total_amount_taken = db.session.query(func.sum(Debt.amount)).filter(
        Debt.user_id == current_user.id,
        Debt.date_taken >= start_date,
        Debt.date_taken <= end_date
    ).scalar()

    if total_amount_taken is None:
        total_amount_taken = 0
    
    income_totals['Debt Taken'] = total_amount_taken

    income_totals['Settled credit'] = total_amount_paid
  
    # Calculate the total income
    total_income = sum(income_totals.values())

    # Initialize lists to store labels, values, and colors for the income chart
    income_labels = []
    income_values = []
    income_colors = ['#ffb65d', '#465bca', '#9d3171', '#3eeed0', '#ff5497', '#309a6a', '#141c33']

    income_chart_data = {
        'labels': income_labels,
        'values': income_values,
        'colors': income_colors,
    }

    # Format the amount values and update the income_totals dictionary
    for category, amount in income_totals.items():
        try:
            percentage = "{:.2f}".format((amount / total_income) * 100)
        except:
            percentage = "{:.2f}".format(0)
        income_labels.append(category)
        income_values.append(percentage)

    # Cash Out trend chart
    today = date.today()
    start_date = date(today.year, today.month, 1)

    # Calculate the end dates for each week
    end_date1 = start_date + timedelta(days=6)
    end_date2 = start_date + timedelta(days=13)
    end_date3 = start_date + timedelta(days=20)
    end_date4 = start_date + timedelta(days=27)

    # Calculate the total cash-out for each week
    total_cash_out1 = db.session.query(func.sum(CashOut.amount)).filter(
        CashOut.user_id == current_user.id,
        CashOut.date >= start_date,
        CashOut.date <= end_date1
    ).scalar()

    total_cash_out2 = db.session.query(func.sum(CashOut.amount)).filter(
        CashOut.user_id == current_user.id,
        CashOut.date >= end_date1 + timedelta(days=1),
        CashOut.date <= end_date2
    ).scalar()

    total_cash_out3 = db.session.query(func.sum(CashOut.amount)).filter(
        CashOut.user_id == current_user.id,
        CashOut.date >= end_date2 + timedelta(days=1),
        CashOut.date <= end_date3
    ).scalar()

    total_cash_out4 = db.session.query(func.sum(CashOut.amount)).filter(
        CashOut.user_id == current_user.id,
        CashOut.date >= end_date3 + timedelta(days=1),
        CashOut.date <= end_date4
    ).scalar()

    cash_out_labels = [f"Week 1",
                       f"Week 2",
                       f"Week 3",
                       f"Week 4"]

    cash_out_values = [total_cash_out1 or 0, total_cash_out2 or 0, total_cash_out3 or 0, total_cash_out4 or 0]

    cash_out_chart_data = {
        'labels': cash_out_labels,
        'values': cash_out_values,
    }

    chart_data = {
        'expense_chart_data': expense_chart_data,
        'income_chart_data': income_chart_data,
        'cash_out_chart_data': cash_out_chart_data 
    }

    return jsonify(chart_data)

@login_required
@app.route('/dashboard', methods=['GET'])
def dashboard():
    """
    Render the user's Dashboard.

    Returns:
        str: The rendered HTML template for the user's dashboard.
    """
    if current_user.is_authenticated:
        # Get the user ID
        user_id = current_user.id

        user = User.query.get(user_id).first_name

        # Calculate total income and individual income transactions for the current month
        total_income, income_transactions = calculate_total_income_between_dates(user_id)

        # Calculate total expenses and individual expense transactions for the current month
        total_expenses, expense_transactions = calculate_total_expenses_between_dates(user_id)

        # Merge income and expense transactions, and sort them by date
        all_transactions = income_transactions + expense_transactions
        all_transactions.sort(key=lambda x: x['date'])
        
        # Calculate total balance
        total_balance = total_income - total_expenses

        return render_template('dashboard.html', 
                               total_income=total_income, 
                               total_expenses=total_expenses, 
                               total_balance=total_balance, 
                               transactions=all_transactions, 
                               username=user)
    else:
        return redirect(url_for('login'))

# Income Magement ------------------------------------------------------------------------
@login_required
@app.route('/income', methods=['GET', 'POST'])
def income():
    """
    Handle user income management.

    Returns:
        str: The rendered HTML template for income management.
    """
    user_id = current_user.id

    if request.method == 'POST':
        '''
        Filter Income transactions by category
        '''
        try:
            category_name = request.json.get('category_name')
            

            # Find the income category ID for the given category name and current user
            if   category_name == 'Debt':
                income_category = Income.query.filter_by(user_id=1, name=category_name).first()
            elif category_name == 'Settled Credit':
                income_category = Income.query.filter_by(user_id=1, name=category_name).first()
            else:
                income_category = Income.query.filter_by(user_id=user_id, name=category_name).first()

            if income_category:
                income_category_id = income_category.id

                # Query CashIn transactions for the specified income category ID and user ID
                transactions = CashIn.query.filter_by(income_id=income_category_id, user_id=user_id).all()
                
                total = 0
                # Extract the required fields from the transactions
                transaction_data = []
                for transaction in transactions:
                    total += transaction.amount
                    transaction_data.append({
                        'id': transaction.id,
                        'category': category_name,
                        'amount': "{:,.2f}/=".format(float(transaction.amount)),
                        'date': transaction.date.strftime('%Y-%m-%d'),
                        'description': transaction.description
                    })

                return jsonify({'transactions': transaction_data, 
                                'total': "{:,.2f}/=".format(total)
                                }), 200
            
            else:
                return jsonify({'error': 'Category not found for the current user'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500


    category_form = IncomeCategoryForm()
    transaction_form = IncomeTransactionForm()

    # Query all IncomeType records (shared among all users) and Populate the incomeType field
    income_types = IncomeType.query.all()
    category_form.incomeType.choices = [(it.id, it.name) for it in income_types]


    # Query Income categories for the current user and Populate the incomeCategory field
    income_categories = Income.query.filter_by(user_id=current_user.id).all()
    transaction_form.incomeCategory.choices = [(ic.id, ic.name) for ic in income_categories]

    # Calculates total income including debt
    income_totals = calculate_income_totals_formatted_debt(current_user.id)

    total_income, individual_incomes = calculate_total_income_between_dates(current_user.id)

    # Prepare the data in the desired format
    income_transactions = [
        {
            'transaction_id': income['id'],
            'income_category_name': income['name'],
            'income_category_id': income['income_category_id'],
            'description': income['description'],
            'date': income['date'].strftime('%Y-%m-%d'),
            'amount': "{:,.2f}/=".format(income['amount']),
        }
        for income in individual_incomes
    ]

    # Get the beginning of the month and current date in the desired format
    today = date.today()
    start_of_month = date(today.year, today.month, 1)
    from_date_formatted = start_of_month.strftime('%b %d, %Y')
    to_date_formatted = today.strftime('%b %d, %Y')

    return render_template('income.html', 
                           category_form=category_form, 
                           transaction_form=transaction_form,
                           income_types=income_types, # create income category form
                           income_categories=income_categories, # form data
                           income_totals=income_totals, # card data
                           income_transactions=income_transactions, # Table
                           total_income="{:,.2f}/=".format(total_income), # Summary
                           from_date=from_date_formatted, # summary
                           to_date=to_date_formatted)  # summary

# create an income category
@login_required
@app.route('/create_income_category', methods=['POST'])
def create_income_category():
    """
    Create a new income category.

    Returns:
        json: JSON response indicating success or an error message.
    """

    if request.method == 'POST':
        # Handle the form data here
        category_name = request.form.get('categoryName')
        income_type_id = request.form.get('incomeType')

        # Get the current user's ID
        user_id = current_user.id

        # Call the add_income function to insert the income category
        result, income = add_income(user_id, category_name, income_type_id)

        if result is True:
            if income:
                category_id = income.id
                response_data = {
                    'message': 'Category created successfully',
                    'category_name': category_name,
                    'category_id': category_id 
                }
                return jsonify(response_data), 200
            else:
                # Handle the case where the category was not found
                return jsonify({'error': 'Category not found'}), 404
        else:
            # Handle the error case
            response_data = {'error': result}  # 'result' contains the error message
            return jsonify(response_data), 400
    else:
        # Handle other HTTP methods if needed
        return abort(405)

# Create an income transaction
@login_required
@app.route('/create_income_transaction', methods=['POST'])
def create_income_transaction():
    # Get form data from the request
    income_category = request.form.get('incomeCategory')
    amount = request.form.get('amount')
    date = request.form.get('date')
    debtor = request.form.get('debtor')
    description = request.form.get('description')

    # Convert income_category and amount to appropriate data types (e.g., int, float)
    try:
        income_category = int(income_category)
        amount = float(amount)
    except ValueError:
        return jsonify({'error': 'Invalid data provided'}), 400
    
    # Convert the date string to a Python date object
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date provided'}), 400

    # Handle validation and creation of the income transaction
    try:
        user_id = current_user.id

        # Query the Credit model to find the appropriate credit using debtor and user_id
        credit_to_settle = Credit.query.filter_by(debtor=debtor, user_id=user_id, is_paid=False).first()

        if not credit_to_settle and income_category == 1:
            raise ValueError("No outstanding credit found for the specified debtor.")

        # Call the add_cash_in_transaction function with the settled_credit_id
        cash_in = add_cash_in_transaction(
            user_id=user_id,
            amount=amount,
            date=date_obj,
            income_id=income_category,
            description=description,
            settled_credit_id=credit_to_settle.id if credit_to_settle else None
        )

        if credit_to_settle:
            credit = Credit.query.filter_by(id=credit_to_settle.id, user_id=current_user.id).first()
            if not credit:
                return jsonify({"error": "Credit not found or unauthorized"}), 403

            '''if credit.is_paid:
                return jsonify({"error": "Credit is already paid"}), 400'''

            payment = DebtorPayment(credit_id=credit.id, amount=amount, date=date_obj)
            db.session.add(payment)

            credit.amount_paid += Decimal(amount)

            if credit.amount_paid >= credit.amount:
                credit.is_paid = True

            db.session.commit()

        income_category_name = Income.query.get(income_category).name
        # Construct the JSON response with all required information
        response_data = {
            'message': 'Income transaction created successfully',
            'transaction_id': cash_in.id,
            'income_category_name': income_category_name,
            'amount': "{:,.2f}/=".format(amount),
            'description': description,
            'date': date,
        }

        return jsonify(response_data), 201

    except ValueError as e:
        # Handle validation errors
        return jsonify({'error': str(e)}), 400

@app.route('/search_income_transactions', methods=['GET'])
@login_required
def search_income_transactions():
    '''
    Search Income transactions by date
    '''
    user_id = current_user.id 
    start_date_str = request.args.get('from')
    end_date_str = request.args.get('to')

    try:
        # Convert date strings to date objects with 'yyyy-mm-dd' format
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        total_income, individual_incomes = calculate_total_income_between_dates(user_id, start_date, end_date)
        income_totals = calculate_income_totals_formatted_debt(user_id, start_date, end_date)

        response_data = {
            'total_income': str(total_income),  # Convert Decimal to string
            'individual_incomes': individual_incomes,
            'income_totals': income_totals
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Route to edit an income transaction
@app.route('/edit_income_transaction', methods=['POST'])
@login_required
def edit_income_transaction():
    # Parse JSON data sent from the client (JavaScript)
    data = request.get_json()

    # Extract data from the JSON request
    transaction_id = data.get('transaction_id')
    new_date_str = data.get('new_date')  # Date as string
    new_amount = data.get('new_amount')
    new_description = data.get('new_description')
    new_category_id = data.get('new_category_id')

    # Check if all required fields are provided
    if not (new_date_str and new_amount and new_category_id):
        return jsonify({'error': 'Please provide all required fields.'}), 400

    # Convert new_date_str to a Python date object
    try:
        new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD format.'}), 400

    # Check if the date is not in the future
    if new_date > datetime.now().date():
        return jsonify({'error': 'Please select a date that is not in the future.'}), 400

    # Check if the amount is non-negative
    if new_amount < 0:
        return jsonify({'error': 'Please enter a non-negative amount.'}), 400

    # Check if description is provided and not longer than 100 characters
    if new_description:
        if len(new_description) > 100:
            return jsonify({'error': 'Description should not exceed 100 characters.'}), 400

    # Query the database to ensure the transaction and category exist
    transaction = CashIn.query.get(transaction_id)
    if not transaction:
        return jsonify({'error': 'Transaction not found.'}), 404

    category = Income.query.get(new_category_id)
    if not category:
        return jsonify({'error': 'Income category not found.'}), 404

    # Perform the edit operation on the transaction using the CashIn model
    try:
        transaction.update_transaction(new_description, new_amount, new_date, new_category_id)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error editing the transaction.'}), 500

    new_category_name = Income.query.get(transaction.income_id).name

    # Return the edited transaction details in the response
    edited_transaction = {
        'transaction_id': transaction.id,
        'new_date': transaction.date.strftime('%Y-%m-%d'),
        'new_amount': "{:,.2f}/=".format(transaction.amount),
        'new_description': transaction.description,
        'new_category_id': transaction.income_id,
        'new_category_name': new_category_name,
    }

    return jsonify({'message': 'Income transaction updated successfully', 'edited_transaction': edited_transaction}), 200

# Route to delete an income transaction
@app.route('/delete_income_transaction', methods=['POST'])
@login_required
def delete_income_transaction():
    # Parse JSON data sent from the client (JavaScript)
    data = request.get_json()

    # Extract data from the JSON request
    transaction_id = data.get('transaction_id')

    # Query the database to find the transaction using CashIn model
    transaction = CashIn.query.get(transaction_id)

    if not transaction:
        # Transaction not found, return an error response
        return jsonify({'error': 'Transaction not found.'}), 404

    try:
        # Use the CashIn model method to delete the transaction
        transaction.delete_transaction()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error deleting the transaction.'}), 500

    # Return a response indicating success
    return jsonify({'message': 'Income transaction deleted successfully'}), 200


# Expense Magement ------------------------------------------------------------------------
@app.route('/expense', methods=['GET', 'POST'])
@login_required
def expense():
    if request.method == 'GET':

        # Query Income categories for the current user
        expense_categories = Expense.query.filter_by(user_id=current_user.id).all()

        # Query the contribution of each category to the user's total expense
        expense_totals = calculate_expense_totals(current_user.id)

        '''
        Include credit and settled debt as categories that take out Income
        '''
        today = date.today()
        start_date = date(today.year, today.month, 1)
        end_date = date.today()

        # settled debt amount
        total_amount_paid = db.session.query(func.sum(Debt.amount_payed)).filter(
            Debt.user_id == current_user.id,
            Debt.date_taken >= start_date,
            Debt.date_taken <= end_date
        ).scalar()

        if total_amount_paid is None:
            total_amount_paid = 0 

        # credit given amount
        total_amount_given = db.session.query(func.sum(Credit.amount)).filter(
            Credit.user_id == current_user.id,
            Debt.date_taken >= start_date,
            Debt.date_taken <= end_date
        ).scalar()

        if total_amount_given is None:
            total_amount_given = 0 

        expense_totals['Settled Debt'] = total_amount_paid
        expense_totals['Credit'] = total_amount_given
    

        # Initialize a dictionary to store formatted amounts and percentages
        formatted_expense_totals = {}

        # Calculate the total income
        total_expense = sum(expense_totals.values())

        # Format the amount values and update the income_totals dictionary
        for category, amount in expense_totals.items():
            formatted_amount = "{:,.2f}/=".format(amount)
            try:
                percentage = "{:.2f}".format((amount / total_expense) * 100)
            except:
                percentage = "{:.2f}".format(0)
            formatted_expense_totals[category] = (formatted_amount, percentage)

        # Replace the original income_totals dictionary with the formatted one
        expense_totals = formatted_expense_totals

        # Call the calculate_total_income_between_dates function
        total_expenses, individual_expenses = calculate_total_expenses_between_dates(current_user.id)

        # Prepare the data in the desired format
        expense_transactions = [
            {
                'transaction_id': exp['id'],
                'expense_category_name': exp['name'],
                'expense_category_id': exp['expense_category_id'],
                'description': exp['description'],
                'date': exp['date'].strftime('%Y-%m-%d'),
                'amount': "{:,.2f}/=".format(exp['amount']), 
            }
            for index, exp in enumerate(individual_expenses)
        ]

        # Get the beginning of the month and current date in the desired format
        today = date.today()
        start_of_month = date(today.year, today.month, 1)
        from_date_formatted = start_of_month.strftime('%b %d, %Y')
        to_date_formatted = today.strftime('%b %d, %Y')

        # Load the expense trmplate
        return render_template('expense.html', 
                               expense_categories = expense_categories,
                               expense_totals = expense_totals,
                               expense_transactions = expense_transactions, 
                               total_expenses = "{:,.2f}/=".format(total_expenses),
                               from_date=from_date_formatted,
                               to_date=to_date_formatted
                               )
    else:
        '''
        Filter Income transactions by category
        '''
        try:
            # Handle AJAX POST request to retrieve transactions by category
            category_name = request.json.get('category_name')

            user_id = current_user.id

            # Find the expense category ID for the given category name and current user
            if   category_name == 'Credit':
                expense_category = Expense.query.filter_by(user_id=1, name=category_name).first()
            elif   category_name == 'Settled Debt':
                expense_category = Expense.query.filter_by(user_id=1, name=category_name).first()
            else:
                expense_category = Expense.query.filter_by(user_id=user_id, name=category_name).first()

            if expense_category:
                if category_name == 'Credit':
                    expense_category_id = 1

                else:
                    expense_category_id = expense_category.id

                # Query CashOut transactions for the specified expense category ID and user ID
                transactions = CashOut.query.filter_by(expense_id=expense_category_id, user_id=user_id).all()

                total_expenses = 0

                # Extract the required fields from the transactions
                transaction_data = []
                for transaction in transactions:
                    transaction_data.append({
                        'id': transaction.id,
                        'category': category_name,
                        'amount': "{:,.2f}/=".format(float(transaction.amount)),
                        'date': transaction.date.strftime('%Y-%m-%d'),
                        'description': transaction.description
                    })
                    total_expenses += transaction.amount

                return jsonify({'transactions': transaction_data,
                                'total_expenses':"{:,.2f}/=".format(total_expenses)
                                })
            
            else:
                return jsonify({'error': 'Category not found for the current user'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/create_expense_category', methods=['POST'])
@login_required
def create_expense_category():
    # Get the user ID from the current_user object provided by Flask-Login
    user_id = current_user.id

    # Get the category name from the request data
    data = request.get_json()
    expense_name = data.get('categoryName')

    if not expense_name:
        return jsonify({"success": False, "message": "Category name cannot be empty."}), 400

    if len(expense_name) > 100:
        return jsonify({"success": False, "message": "Category name cannot exceed 100 characters."}), 400

    # Attempt to add the expense category
    result = add_expense(user_id, expense_name)

    if isinstance(result, Expense):
        # Expense category added successfully
        expense = result
        return jsonify({"success": True, "name": expense.name, "id": expense.id})

    # Handle the case where an error occurred while adding the expense
    return jsonify({"success": False, "message": "An error occurred while adding the expense."}), 500

@login_required
@app.route('/create_expense_transaction', methods=['POST'])
def create_expense_transaction():
    # Get form data from the request
    expense_category = request.form.get('expenseCategory')
    amount = request.form.get('amount')
    date = request.form.get('date')
    creditor = request.form.get('creditor')
    description = request.form.get('description')

    # Convert income_category and amount to appropriate data types (e.g., int, float)
    try:
        expense_category = int(expense_category)
        amount = float(amount)
    except ValueError:
        return jsonify({'error': 'Invalid data provided'}), 400
    
    # Convert the date string to a Python date object
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date provided'}), 400

    # Handle validation and creation of the expense transaction
    try:
        user_id = current_user.id

        # Check if the budget for the current month and year exists
        current_month = datetime.now().month
        current_year = datetime.now().year
 
        current_budget = Budget.query.filter_by(user_id=user_id, month=current_month, year=current_year).first()

        if current_budget:
            # Check if the expense is listed in the current month's BudgetExpense
            budget_expense = BudgetExpense.query.filter_by(budget_id=current_budget.id, expense_id=expense_category).first()
            if budget_expense:
                print('Budget Expense before transaction', budget_expense.spent_amount)
                try:
                    amount = int(amount) if amount else 0.0
                    budget_expense.update_spent_amount(amount)
                    db.session.commit()
                    print('Budget Expense after transaction', budget_expense.spent_amount)
                except Exception as e:
                    print('Budget Expense not updated')
                    db.session.rollback() 

        # Call the add_cash_out_transaction function with the settled_credit_id
        cash_out = add_cash_out_transaction(
            user_id=user_id,
            amount=amount,
            date=date_obj,
            expense_id=expense_category,
            description=description,
        )

        expense_category_name = Expense.query.get(expense_category).name

        # Construct the JSON response with all required information
        response_data = {
            'message': 'Expense transaction created successfully',
            'transaction_id': cash_out.id,
            'expense_category_name': expense_category_name,
            'amount': "{:,.2f}/=".format(amount),
            'description': description,
            'date': date,
        }

        return jsonify(response_data), 201

    except ValueError as e:
        # Handle validation errors
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        # Handle other errors
        return jsonify({'error': 'An error occurred while creating the income transaction'}), 500

@app.route('/search_expense_transactions', methods=['GET'])
@login_required
def search_expense_transactions():
    '''
    Search Expense transactions by date
    '''
    user_id = current_user.id 
    start_date_str = request.args.get('from')
    end_date_str = request.args.get('to')

    try:
        # Convert date strings to date objects with 'yyyy-mm-dd' format
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        total_expense, individual_expenses = calculate_total_expenses_between_dates(
            user_id, start_date, end_date
        )

        # Query the contribution of each category to the user's total expense
        expense_totals = calculate_expense_totals(current_user.id, start_date, end_date)

        '''
        Include credit as a category that contributes to expense
        '''
        # Sum the credit given in the date period
        total_amount_given = db.session.query(func.sum(Credit.amount)).filter(
            Credit.user_id == user_id,
            Credit.date_taken >= start_date,
            Credit.date_taken <= end_date
        ).scalar()

        if total_amount_given is None:
            total_amount_given = 0

        # Add the total_credit_amount to the expense_totals dictionary with 'Credit' as the key
        expense_totals['Credit'] = total_amount_given

        '''
        Include settled debt as a category that contributes to expense
        '''
        total_amount_paid = db.session.query(func.sum(CashOut.amount)).filter(
            CashOut.expense_id==2,
            CashOut.user_id == user_id,
            CashOut.date >= start_date,
            CashOut.date <= end_date
        ).scalar()

        if total_amount_paid is None:
            total_amount_paid = 0 
        
        expense_totals['Settled Debt'] = total_amount_paid
    

        # Initialize a dictionary to store formatted amounts and percentages
        formatted_expense_totals = {}

        # Calculate the total income
        total_expense = sum(expense_totals.values())

        # Format the amount values and update the expense_totals dictionary
        for category, amount in expense_totals.items():
            formatted_amount = "{:,.2f}/=".format(amount)
            try:
                percentage = "{:.2f}".format((amount / total_expense) * 100)
            except:
                percentage = "{:.2f}".format(0)
            formatted_expense_totals[category] = (formatted_amount, percentage)

        # Replace the original expense_totals dictionary with the formatted one
        expense_totals = formatted_expense_totals

        response_data = {
            'total_expense': str(total_expense),
            'individual_expenses': individual_expenses,
            'expense_totals': expense_totals
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/edit_expense_transaction', methods=['POST'])
@login_required
def edit_expense_transaction():
    # Parse JSON data sent from the client (JavaScript)
    data = request.get_json()

    # Extract data from the JSON request
    transaction_id = data.get('transaction_id')
    new_date_str = data.get('new_date')
    new_amount = data.get('new_amount')
    new_description = data.get('new_description')
    expense_id = data.get('expense_id')
    amount_diff = data.get('amount_diff')

    # Check if all required fields are provided
    if not (new_date_str and new_amount):
        return jsonify({'error': 'Please provide all required fields.'}), 400

    # Convert new_date_str to a Python date object
    try:
        new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD format.'}), 400

    # Check if the date is not in the future
    if new_date > datetime.now().date():
        return jsonify({'error': 'Please select a date that is not in the future.'}), 400

    # Check if the amount is non-negative
    if new_amount < 0:
        return jsonify({'error': 'Please enter a non-negative amount.'}), 400

    # Check if description is provided and not longer than 100 characters
    if new_description:
        if len(new_description) > 100:
            return jsonify({'error': 'Description should not exceed 100 characters.'}), 400

    # Query the database to ensure the transaction and category exist
    transaction = CashOut.query.get(transaction_id)
    if not transaction:
        return jsonify({'error': 'Transaction not found.'}), 404
    
    # Extract month and year from the new date
    new_month = get_month_name(new_date.month)
    new_year = new_date.year

    # Find the current user's budget for the same month and year, if it exists
    budget = Budget.query.filter_by(
        user_id=current_user.id,
        month=new_month,
        year=new_year
    ).first()

    if budget:
        # Find the BudgetExpense entry with the same budget and expense_id
        budget_expense = BudgetExpense.query.filter_by(
            budget_id=budget.id,
            expense_id=expense_id
        ).first()
 
        if budget_expense:
            try:     
                # Update the spent amount in BudgetExpense using the amount_diff
                if amount_diff < 0:
                    budget_expense.spent_amount -= abs(amount_diff)
                elif amount_diff > 0:
                    budget_expense.update_spent_amount(amount_diff)
                db.session.commit()

            except Exception as e:
                db.session.rollback()
                return jsonify({'error': 'Error updating the spent amount in BudgetExpense.'}), 500

    # Perform the edit operation on the transaction using the CashOut model
    try:
        transaction.update_transaction(new_description, new_amount, new_date, int(expense_id))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error editing the transaction.'}), 500
    
    new_category_name = Expense.query.get(transaction.expense_id).name
    # Return the edited transaction details in the response
    edited_transaction = {
        'transaction_id': transaction.id,
        'new_date': transaction.date.strftime('%Y-%m-%d'),
        'new_amount': "{:,.2f}/=".format(transaction.amount),
        'new_description': transaction.description,
        'new_category_id': transaction.expense_id,
        'new_category_name': new_category_name,
    }

    return jsonify({'message': 'Expense transaction updated successfully', 'edited_transaction': edited_transaction}), 200

@app.route('/delete_expense_transaction', methods=['POST'])
@login_required
def delete_expense_transaction():
    # Parse JSON data sent from the client (JavaScript)
    data = request.get_json()

    # Extract data from the JSON request
    transaction_id = data.get('transaction_id')

    # Query the database to find the transaction using CashOut model
    transaction = CashOut.query.get(transaction_id)

    if not transaction:
        # Transaction not found, return an error response
        return jsonify({'error': 'Transaction not found.'}), 404

    try:
        # Check if the transaction is associated with a budget
        if transaction.date and transaction.expense_id:
            # Extract the month and year from the transaction's date
            transaction_month = transaction.date.month
            transaction_year = transaction.date.year

            # Find the corresponding budget
            budget = Budget.query.filter_by(
                user_id=current_user.id,
                month=transaction_month,
                year=transaction_year
            ).first()

            if budget:
                # Find the BudgetExpense entry with the same budget and expense_id
                budget_expense = BudgetExpense.query.filter_by(
                    budget_id=budget.id,
                    expense_id=transaction.expense_id
                ).first()

                if budget_expense:
                    # Subtract the transaction amount from spent_amount
                    budget_expense.spent_amount -= transaction.amount
                    db.session.commit()

        # Use the CashOut model method to delete the transaction
        transaction.delete_transaction()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error deleting the transaction.'}), 500

    # Return a response indicating success
    return jsonify({'message': 'Expense transaction deleted successfully'}), 200


# Budget Magement ------------------------------------------------------------------------
def get_month_name(month_number):
    # Map month numbers to their names
    month_names = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    # Ensure month_number is within a valid range
    if 1 <= month_number <= 12:
        return month_names[month_number - 1]
    else:
        return None  # Return None for invalid month numbers
    
@app.route('/budget', methods=['GET', 'POST'])
@login_required
def budget():
    user_id = current_user.id

    # Get the current year and month
    current_year = int(datetime.now().year)
    current_month = int(datetime.now().month)

    # Handle POST request to create a budget
    if request.method == 'POST':
        # Create a new budget for the current month and year
        new_budget = create_budget(user_id, current_year, current_month)

        # Return the newly created budget object in JSON format
        return jsonify({
            'id': new_budget.id,
            'user_id': new_budget.user_id,
            'year': new_budget.year,
            'month': new_budget.month
        })
    

    # Query for all expenses for the current user
    expenses = Expense.query.filter_by(user_id=user_id).all()

    # Query for all budgets created by the user
    budgets = Budget.query.filter_by(user_id=user_id).all()

    budget_with_totals = []

    # Calculate total expected and actual amounts for each budget
    for budget in budgets:
        # Query for budget expenses associated with the current budget
        budget_expenses = BudgetExpense.query.filter_by(budget_id=budget.id).all()

        total_expected_amount = sum(budget_expense.expected_amount for budget_expense in budget_expenses)
        total_actual_amount = sum(budget_expense.spent_amount for budget_expense in budget_expenses)

        budget_with_totals.append({
            'id': budget.id,
            'user_id': budget.user_id,
            'year': budget.year,
            'month': budget.month,
            'total_expected_amount': total_expected_amount,
            'total_actual_amount': total_actual_amount
        })

    current_budget = Budget.query.filter_by(user_id=user_id, year=current_year, month=current_month).first()

    budget_expenses_with_names = []
    current_total_expected_amount = 0
    current_total_actual_amount = 0
    expense_count = 0

    # If a current budget exists, query for its expenses and join with expense names
    if current_budget:
        # Calculate the start and end dates for the current month
        start_date = date(current_year, current_month, 1)
        end_date = date.today()
        budget_expenses = BudgetExpense.query.filter_by(budget_id=current_budget.id).all()
        
        # Join budget expenses with expense names
        for budget_expense in budget_expenses:
            expense_count += 1
            expense = Expense.query.get(budget_expense.expense_id)
            total_spent_amount = db.session.query(func.sum(CashOut.amount)).filter(
                CashOut.user_id == user_id,
                CashOut.expense_id == expense.id,
                CashOut.date >= start_date,
                CashOut.date <= end_date
            ).scalar()

            # Update the spent amount for the BudgetExpense
            if budget_expense.spent_amount == 0:
                amt = total_spent_amount if total_spent_amount else 0.0
                budget_expense.update_spent_amount(amt)
                db.session.commit()

            budget_expense=BudgetExpense.query.get(budget_expense.id)
            budget_expenses_with_names.append({
                'id': budget_expense.id,
                'budget_id': budget_expense.budget_id,
                'expense_id': budget_expense.expense_id,
                'expected_amount': budget_expense.expected_amount,
                'spent_amount': budget_expense.spent_amount,
                'expense_name': expense.name
            })

        current_total_expected_amount += sum(budget_expense.expected_amount for budget_expense in budget_expenses)
        current_total_actual_amount += sum(budget_expense.spent_amount for budget_expense in budget_expenses)

    # Define a dictionary to map month numbers to month names
    months = {
        1: 'January',
        2: 'February',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December'
    }
    return render_template('budget.html', expenses=expenses, 
                           current_budget=current_budget, 
                           budget_expenses=budget_expenses_with_names,
                           budgets=budget_with_totals,
                           current_total_expected_amount=current_total_expected_amount,
                           current_total_actual_amount=current_total_actual_amount,
                           expense_count=expense_count,
                           months=months
                           )

@app.route('/create_budget_expense', methods=['POST'])
@login_required
def create_budget_expense():
    try:
        data = request.get_json()
        expense_id = data.get('expense_id')
        expected_amount = data.get('expected_amount')
        budgetId = data.get('budgetId')

        # Validate data (ensure expense_id exists and expected_amount is non-negative)
        if not expense_id or not budgetId or expected_amount is None or expected_amount < 0:
            return jsonify({'error': 'Invalid data'}), 400

        # Create a new BudgetExpense record
        budget_expense = BudgetExpense(
            budget_id=budgetId,
            expense_id=expense_id,
            expected_amount=expected_amount,
            spent_amount=0.0
        )

        # Add the new budget expense to the database and commit the transaction
        db.session.add(budget_expense)
        db.session.commit()

        # Get the related expense and budget information
        expense = Expense.query.get(expense_id)
        budget = Budget.query.get(budgetId)

        # Prepare the JSON response with additional data
        response_data = {
            'message': 'Budget expense created successfully',
            'expense_id': expense.id,
            'expense_name': expense.name,
            'budget_id': budget.id,
            'budget_expense_id': budget_expense.id,
            'expected_amount': "{:,.2f}/=".format(budget_expense.expected_amount),
            'actual_amount': "{:,.2f}/=".format(0.00)
        }

        # Return the JSON response
        return jsonify(response_data), 200

    except Exception as e:
        # Handle exceptions or errors here
        return jsonify({'error': str(e)}), 500
    
@app.route('/search_budget_expenses/<int:budget_id>', methods=['GET'])
@login_required
def search_budget_expenses(budget_id):
    try:
        # Check if the budget exists
        budget = Budget.query.get(budget_id)
        if not budget:
            return jsonify({'error': 'Budget not found'}), 404

        # Query for BudgetExpense records associated with the budget ID
        budget_expenses = BudgetExpense.query.filter_by(budget_id=budget_id).all()

        # Calculate the sum of expected and spent amounts
        total_expected_amount = sum(expense.expected_amount for expense in budget_expenses)
        total_spent_amount = sum(expense.spent_amount for expense in budget_expenses)
        expense_count = 0

        # Prepare the data to send back to the client
        budget_expenses_data = []
        for expense in budget_expenses:
            expense_count += 1
            budget_expenses_data.append({
                'id': expense.id,
                'budget_id': expense.budget_id,
                'expense_id': expense.expense_id,
                'expected_amount':  "{:,.2f}/=".format(expense.expected_amount),
                'spent_amount':  "{:,.2f}/=".format(expense.spent_amount),
                'percentage': "{:.2f}".format((expense.spent_amount / expense.expected_amount) * 100),
                'expense_name': Expense.query.get(expense.expense_id).name  # Get the expense name
            })

        if isinstance(budget.month, int):
            budget.month = get_month_name(budget.month)
        return jsonify({
            'budget_expenses': budget_expenses_data,
            'total_expected_amount': total_expected_amount,
            'total_spent_amount': total_spent_amount,
            'percent': "{:.2f}%".format((total_spent_amount / total_expected_amount) * 100),
            'expense_count': expense_count,
            'year': budget.year,
            'month': budget.month,
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search_budget_by_year_month', methods=['POST'])
@login_required
def search_budget_by_year_month():
    # Get the year and month from the request JSON data
    data = request.get_json()
    year = data.get('year')
    month = data.get('month')

    month = int(month)
    
    try:
        # Query for the budget with the specified year and month
        budget = Budget.query.filter_by(year=year, month=month, user_id=current_user.id).first()
        if not budget:
            return jsonify({'error': 'Budget not found for the specified year and month'}), 404

        # Query for BudgetExpense records associated with the budget ID
        budget_expenses = BudgetExpense.query.filter_by(budget_id=budget.id).all()

        # Calculate the sum of expected and spent amounts
        total_expected_amount = sum(expense.expected_amount for expense in budget_expenses)
        total_spent_amount = sum(expense.spent_amount for expense in budget_expenses)

        expense_count = 0
        # Prepare the data to send back to the client
        budget_expenses_data = []
        for expense in budget_expenses:
            expense_count += 1
            budget_expenses_data.append({
                'id': expense.id,
                'budget_expense_id': expense.id,
                'budget_id': expense.budget_id,
                'expense_id': expense.expense_id,
                'expected_amount': "{:,.2f}/=".format(expense.expected_amount),
                'spent_amount':  "{:,.2f}/=".format(expense.spent_amount),
                'percentage': "{:.2f}".format((expense.spent_amount / expense.expected_amount) * 100),
                'expense_name': Expense.query.get(expense.expense_id).name 
            })

        return jsonify({
            'budget_id': budget.id,
            'year': budget.year,
            'month': budget.month,
            'budget_expenses': budget_expenses_data,
            'total_expected_amount': total_expected_amount,
            'total_spent_amount': total_spent_amount,
            'percent': "{:.2f}%".format((total_spent_amount / total_expected_amount) * 100),
            'expense_count': expense_count
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/edit_budget_expense', methods=['POST'])
@login_required
def edit_budget_expense():
    try:
        data = request.get_json()
        budget_expense_id = data['budget_expense_id']
        budget_id = data['budget_id']
        expenseId = data['expenseId']
        edited_expected_amount = data['edited_expected_amount']

        budget_expense = db.session.query(BudgetExpense).filter_by(
            id=budget_expense_id,
            budget_id=budget_id,
            expense_id=expenseId
        ).first()

        if budget_expense:
            # Update the expected amount
            budget_expense.expected_amount = edited_expected_amount
            
            # Commit the changes to the database
            db.session.commit()

            budget_expense = db.session.query(BudgetExpense).filter_by(
                id=budget_expense_id,
                budget_id=budget_id,
                expense_id=expenseId
            ).first()
            edited_expected_amount = "{:,.2f}".format(budget_expense.expected_amount)

            return jsonify({'updated_expected_amount': edited_expected_amount, 
                            'message': 'BudgetExpense edited successfully'}), 200

        else:
            return jsonify({'error': 'BudgetExpense not found'}), 404

    except Exception as e:
        # Handle errors and return an error response
        return jsonify({'error': str(e)}), 500

@app.route('/delete_budget_expense', methods=['POST'])
@login_required
def delete_budget_expense():
    try:
        data = request.get_json()
        budget_expense_id = data['budget_expense_id']

        budget_expense = db.session.query(BudgetExpense).filter_by(id=budget_expense_id).first()

        if budget_expense:
            # Delete the BudgetExpense record
            db.session.delete(budget_expense)
            db.session.commit()

            # Return a success message in the response
            return jsonify({'message': 'BudgetExpense deleted successfully'}), 200

        else:
            return jsonify({'error': 'BudgetExpense not found'}), 404

    except Exception as e:
        # Handle errors and return an error response
        return jsonify({'error': str(e)}), 500
    
# Credit Magement ------------------------------------------------------------------------
@app.route('/credit', methods=['GET', 'POST'])
@login_required
def credit():
    if request.method == 'POST':
        try:
            data = request.get_json()

            # Extract data from JSON
            debtor = data.get('debtor')
            amount = data.get('amount')
            date_taken = data.get('dateTaken')
            date_due = data.get('dateDue')
            description = data.get('description')

            # Trim and convert debtor name to title case
            debtor = titlecase(debtor.strip())

            # Convert the date string to a Python date object
            try:
                date_taken = datetime.strptime(date_taken, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date taken provided'}), 400
            
            if date_due:
                try:
                    date_due = datetime.strptime(date_due, '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'error': 'Invalid date due provided'}), 400

            # Create a new Credit record
            new_credit = Credit(
                user_id=current_user.id,
                debtor=debtor,
                amount=amount,
                date_taken=date_taken,
                date_due=date_due,
                description=description
            )

            # Add and commit the new credit record to the database
            db.session.add(new_credit)

            cash_out = CashOut(
                user_id=current_user.id,
                expense_id=1,
                amount=amount,
                date=date_taken,
                description=description
            )

            db.session.add(cash_out)

            db.session.commit()

            # Return the newly created credit record in JSON format
            response_data = {
                'id': new_credit.id,
                'user_id': new_credit.user_id,
                'debtor': new_credit.debtor,
                'amount': "{:,.2f}/=".format(new_credit.amount),
                'date_taken': new_credit.date_taken.strftime('%Y-%m-%d'),
                'date_due': new_credit.date_due.strftime('%Y-%m-%d') if new_credit.date_due else None,
                'description': new_credit.description,
                'is_paid': new_credit.is_paid,
                'amount_paid': "{:,.2f}/=".format(new_credit.amount_paid)
            }

            return jsonify(response_data), 201  # Return 201 status code for successful creation

        except Exception as e:
            # Handle errors and return an error response
            error_message = str(e)
            return jsonify({'error': error_message}), 400  # Return 400 status code for bad request
    # Fetch all rows in the Credit model for the current user, ordered by date_taken
    credits = Credit.query.filter_by(user_id=current_user.id).order_by(Credit.date_taken.desc()).all()
    total_amount_paid = db.session.query(func.sum(Credit.amount_paid)).filter(
        Credit.user_id == current_user.id,
    ).scalar()

    total_amount_owed = db.session.query(func.sum(Credit.amount)).filter(
        Credit.user_id == current_user.id,
    ).scalar()

    if total_amount_paid is None:
        total_amount_paid = 0 

    if total_amount_owed is None:
        total_amount_owed = 0 
    
    return render_template('credit.html', 
                           credits=credits,
                           total_amount_owed=total_amount_owed,
                           total_amount_paid=total_amount_paid)

@app.route('/credit/settle', methods=['POST'])
@login_required
def settle_credit():
    try:
        data = request.json
        credit_id = int(data['creditId'])
        amount_to_pay = data['amountToPay'] 
        date_paid_str = data['datePaid']
        date_paid = datetime.strptime(date_paid_str, '%Y-%m-%d').date() 

        credit = Credit.query.filter_by(id=credit_id, user_id=current_user.id).first()

        if not credit:
            return jsonify({"error": "Credit not found or unauthorized"}), 403

        if credit.is_paid:
            return jsonify({"error": "Credit is already paid"}), 400

        payment = DebtorPayment(credit_id=credit_id, amount=amount_to_pay, date=date_paid)
        db.session.add(payment)

        credit.amount_paid += amount_to_pay

        if credit.amount_paid >= credit.amount:
            credit.is_paid = True

        # Create a CashIn transaction
        cash_in = CashIn(
            user_id=current_user.id,
            income_id=2,
            amount=amount_to_pay,
            date=date_paid,
            description="settling {}'s credit".format(credit.debtor), 
            settled_credit_id=credit.id
        )
        db.session.add(cash_in)
        db.session.commit()

        progress = round((credit.amount_paid / credit.amount) * 100, 2) 

        return jsonify({
            "amountPaid": "{:,.2f}/=".format(credit.amount_paid),
            "progress": "{}%".format(progress),
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Debt Magement ------------------------------------------------------------------------
@app.route('/debt', methods=['GET', 'POST'])
@login_required
def debt():
    if request.method == 'POST':
        try:
            data = request.get_json()

            # Extract data from JSON
            creditor = data.get('debtor')
            amount = data.get('amount')
            date_taken = data.get('dateTaken')
            date_due = data.get('dateDue')
            description = data.get('description')

            # Trim and convert debtor name to title case
            creditor = titlecase(creditor.strip())

            # Convert the date string to a Python date object
            try:
                date_taken = datetime.strptime(date_taken, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date taken provided'}), 400
            
            if date_due:
                try:
                    date_due = datetime.strptime(date_due, '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'error': 'Invalid date due provided'}), 400

            # Create a new Debt record
            new_debt = Debt(
                user_id=current_user.id,
                creditor=creditor,
                amount=amount,
                date_taken=date_taken,
                date_due=date_due,
                description=description
            )

            # Add and commit the new debt record to the database
            db.session.add(new_debt)

            cash_in = CashIn(
                user_id=current_user.id,
                income_id=1,
                amount=amount,
                date=date_taken,
                description=description
            )

            # Add and commit the new cashin record to the database
            db.session.add(cash_in)  
            db.session.commit()

            # Return the newly created debt record in JSON format
            response_data = {
                'id': new_debt.id,
                'user_id': new_debt.user_id,
                'debtor': new_debt.creditor,
                'amount': "{:,.2f}/=".format(new_debt.amount),
                'date_taken': new_debt.date_taken.strftime('%Y-%m-%d'),
                'date_due': new_debt.date_due.strftime('%Y-%m-%d') if new_debt.date_due else None,
                'description': new_debt.description,
                'is_paid': new_debt.is_paid,
                'amount_paid': "{:,.2f}/=".format(new_debt.amount_payed)
            }

            return jsonify(response_data), 201

        except Exception as e:
            # Handle errors and return an error response
            error_message = str(e)
            return jsonify({'error': error_message}), 400 
         
    # Fetch all rows in the Credit model for the current user, ordered by date_taken
    debits = Debt.query.filter_by(user_id=current_user.id).order_by(Debt.date_taken.desc()).all()

    total_amount_returned = 0

    total_amount_received = 0

    for debit in debits:
        total_amount_received += debit.amount
        total_amount_returned += debit.amount_payed

    if total_amount_returned is None:
        total_amount_returned = 0.00 

    if total_amount_received  is None:
        total_amount_received = 0.00 
    
    return render_template('debt.html', 
                           debits=debits,
                           total_amount_received=total_amount_received,
                           total_amount_returned=total_amount_returned)

@app.route('/debt/settle', methods=['POST'])
@login_required
def settle_debt():
    try:
        data = request.json
        debt_id = int(data['creditId'])
        amount_to_pay = data['amountToPay'] 
        date_paid_str = data['datePaid']
        date_paid = datetime.strptime(date_paid_str, '%Y-%m-%d').date()

        debt = Debt.query.filter_by(id=debt_id, user_id=current_user.id).first()

        if not debt:
            return jsonify({"error": "debt not found or unauthorized"}), 403

        if debt.is_paid:
            return jsonify({"error": "Credit is already paid"}), 400

        payment = CreditorPayment(debt_id=debt_id, amount=amount_to_pay, date=date_paid)
        db.session.add(payment)

        debt.amount_payed += Decimal(amount_to_pay)

        if debt.amount_payed >= debt.amount:
            credit.is_paid = True

        # Create a CashOut transaction
        cash_out = CashOut(
            user_id=current_user.id,
            expense_id=2,
            amount=amount_to_pay,
            date=date_paid,
            description="settling {}'s debt".format(debt.creditor), 
            settled_debt_id=debt.id 
        )

        db.session.add(cash_out)
        db.session.commit()

        progress = round((debt.amount_payed / debt.amount) * 100, 2) 

        return jsonify({
            "amountPaid": "{:,.2f}/=".format(debt.amount_payed),
            "progress": "{}%".format(progress),
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
 
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        initialize_default_income_types()

    app.run(debug=True)


