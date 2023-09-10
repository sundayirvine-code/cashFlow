from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify, abort
from auth import register_user, authenticate_user
from forms import RegistrationForm, LoginForm, IncomeCategoryForm, IncomeTransactionForm
from models import db, initialize_default_income_types, User, Income, IncomeType, Credit, CashIn, Expense, Debt, CashOut
from flask_login import login_required, logout_user, LoginManager, login_user, current_user
from transactions import add_income, add_cash_in_transaction, calculate_income_totals, add_expense, calculate_expense_totals, add_cash_out_transaction
from datetime import date, datetime
from calculations import calculate_total_income_between_dates, calculate_total_expenses_between_dates


# Configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dd2870b0e1e26c313a1944254e35f4f650bbdf6be96b1422d5abf6d26edef933'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

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

# User Dashboard
@login_required
@app.route('/dashboard')
def dashboard():
    """
    Render the user's Dashboard.

    Returns:
        str: The rendered HTML template for the user's dashboard.
    """
    if current_user.is_authenticated:
        # Get the username
        username = request.args.get('username')

        # calculate total expenses

        # calculate total income

        # calculate total balance

        # Income Chart data

        # Expense Chart data

        # Transaction History         
        
        return render_template('dashboard.html', username=username)
    else:
        return redirect(url_for('login'))

# User Income management
@login_required
@app.route('/income', methods=['GET', 'POST'])
def income():
    """
    Handle user income management.

    Returns:
        str: The rendered HTML template for income management.
    """
    if request.method == 'POST':
        '''
        Filter Income transactions by category
        '''
        try:
            # Handle AJAX POST request to retrieve transactions by category
            category_name = request.json.get('category_name')
            print(category_name)

            user_id = current_user.id

            # Find the income category ID for the given category name and current user
            if   category_name == 'Debt':
                income_category = Income.query.filter_by(user_id=0, name=category_name).first()
                print(income_category)
            else:
                income_category = Income.query.filter_by(user_id=user_id, name=category_name).first()

            if income_category:
                if category_name == 'Debt':
                    income_category_id = 1

                else:
                    income_category_id = income_category.id

                print(income_category_id)

                # Query CashIn transactions for the specified income category ID and user ID
                transactions = CashIn.query.filter_by(income_id=income_category_id, user_id=user_id).all()

                # Extract the required fields from the transactions
                transaction_data = []
                for transaction in transactions:
                    transaction_data.append({
                        'id': transaction.id,
                        'category': category_name,
                        'amount': float(transaction.amount),
                        'date': transaction.date.strftime('%Y-%m-%d'),
                        'description': transaction.description
                    })

                return jsonify({'transactions': transaction_data})
            
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
    income_categories.insert(0, Income(id=1, user_id=0, name='Debt'))
    transaction_form.incomeCategory.choices = [(ic.id, ic.name) for ic in income_categories]

    # Query the contribution of each category to the user's total income
    income_totals = calculate_income_totals(current_user.id)

    '''
    Include debt as a category that brings in Income
    '''
    # Query unique debtor names for the current user
    debtor_names = (
        db.session.query(Credit.debtor)
        .filter_by(user_id=current_user.id)
        .distinct()
        .all()
    )

    # Extract the debtor names from the query result and Populate the debtor field
    unique_debtors = [debtor[0] for debtor in debtor_names]
    transaction_form.debtor.choices = [(debtor, debtor) for debtor in unique_debtors]

    '''
    COME BACK HERE WHEN DEALING WITH DEBT
    '''
    # Calculate the sum of amount_payed for each debtor
    debtor_totals = {}
    for debtor_name in unique_debtors:
        total_amount_payed = (
            db.session.query(db.func.sum(Credit.amount_payed))
            .filter_by(user_id=current_user.id, debtor=debtor_name)
            .scalar()
        )
        if total_amount_payed is None:
            total_amount_payed = 0
        debtor_totals[debtor_name] = total_amount_payed

    # Calculate the sum of all amount_payed values in the debtor_totals dictionary
    total_debt_amount = sum(debtor_totals.values())

    # Add the total_debt_amount to the income_totals dictionary with 'Debt' as the key
    income_totals['Debt'] = total_debt_amount
  

    # Initialize a dictionary to store formatted amounts and percentages
    formatted_income_totals = {}

    # Calculate the total income
    total_income = sum(income_totals.values())

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

    '''
    This info is used to porpulate the cards and forms
    '''
    return render_template('income.html', 
                           category_form=category_form, 
                           transaction_form=transaction_form,
                           income_types=income_types, 
                           income_categories=income_categories,
                           income_totals=income_totals)


@app.route('/get_income_transactions', methods=['GET'])
@login_required
def get_income_transactions():
    '''
    get the current months Income transactions. I could take this
    and include it in the income route's GET request then update my 
    income template to process the data
    '''
    # Calculate the start and end dates for the current month
    today = date.today()
    start_date = None
    end_date = None

    # Call the calculate_total_income_between_dates function
    total_income, individual_incomes = calculate_total_income_between_dates(current_user.id, start_date, end_date)

    # Prepare the data in the desired format
    income_transactions = [
        {
            'transaction_id': income['id'],
            'income_category_name': income['name'],
            'description': income['description'],
            'date': income['date'].strftime('%Y-%m-%d'),
            'amount': str(income['amount']),
        }
        for index, income in enumerate(individual_incomes)
    ]

    return jsonify({'income_transactions' : income_transactions, 'total_income': total_income})

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

        income_category_name = Income.query.get(income_category).name

        # Construct the JSON response with all required information
        response_data = {
            'message': 'Income transaction created successfully',
            'transaction_id': cash_in.id,
            'income_category_name': income_category_name,
            'amount': amount,
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

@app.route('/manage_income_transaction/<int:transaction_id>', methods=['PUT', 'DELETE'])
@login_required
def manage_cash_in_transaction(transaction_id):
    cash_in_transaction = CashIn.query.get(transaction_id)
    print(cash_in_transaction, 'test 1')

    if not cash_in_transaction:
        return jsonify({'error': 'Transaction not found'}), 404

    print('test 2: transaction available')
    if request.method == 'PUT':
        try:
            # Get the data from the request JSON
            data = request.get_json()
            print(data, 'test 3 json data exists')
            # Validate and extract the data
            new_description = data.get('description', cash_in_transaction.description)
            print(new_description, 'test 4 new description check')

            new_amount = data.get('amount', cash_in_transaction.amount)
            print(new_amount, 'test 5 new amount check')

            new_date = data.get('date', cash_in_transaction.date)
            print(new_date, 'test 6 new date check')

            # Convert amount to appropriate data types (e.g., int, float)
            try:
                new_amount = float(new_amount)
                print(new_amount, 'test 7 new amount data type check')
            except ValueError:
                return jsonify({'error': 'Invalid data provided'}), 400
            
            # Convert the date string to a Python date object
            try:
                new_date = datetime.strptime(new_date, '%Y-%m-%d').date()
                print(new_description, 'test 8 new date data type check')
            except ValueError:
                return jsonify({'error': 'Invalid date provided'}), 400

            if new_amount < 0:
                print(new_amount, 'test 9 new amount less 0 check')
                return jsonify({'error': 'Amount cannot be negative'}), 400

            # Check if it's a debt payment
            if cash_in_transaction.settled_credit_id is not None:
                print(new_description, 'test 10 this is a debt payment check')
                # Retrieve the associated Credit object
                credit = Credit.query.get(cash_in_transaction.settled_credit_id)

                if credit is None:
                    print(credit, 'test 11 new credit to be settled is available check')
                    return jsonify({'error': 'Associated credit not found'}), 400

                # Check if the credit has been settled
                if credit.is_paid:
                    print(credit.is_paid, 'test 12 has the credit been paid already? check')
                    return jsonify({'error': 'Credit has already been paid'}), 400

                # Check if the new amount + amount_payed exceeds the credit amount
                if new_amount + credit.amount_payed > credit.amount:
                    print('test 13 Payment exceeds credit amount check')
                    return jsonify({'error': 'Payment exceeds credit amount'}), 400

                # Update the amount_payed field of the credit
                credit.amount_payed += new_amount

                # Mark the credit as paid if the amount_payed equals the credit amount
                if credit.amount_payed == credit.amount:
                    credit.is_paid = True

            # Call the update_transaction method
            cash_in_transaction.update_transaction(new_description, new_amount, new_date)

            # Format the date as 'yyyy-mm-dd'
            formatted_date = cash_in_transaction.date.strftime('%Y-%m-%d')

            # Create a dictionary with the updated data
            updated_data = {
                'message': 'Transaction updated successfully',
                'id': cash_in_transaction.id,
                'description': cash_in_transaction.description,
                'amount': cash_in_transaction.amount,
                'date': formatted_date,
            }

            return jsonify({'data': updated_data})

        except Exception as e:
            print('test 14 something else is wrong')
            return jsonify({'error': 'Invalid data format'}), 400

    elif request.method == 'DELETE':
        # Call the delete_transaction method
        cash_in_transaction.delete_transaction()
        return jsonify({'message': 'Transaction deleted successfully'})

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

        total_income, individual_incomes = calculate_total_income_between_dates(
            user_id, start_date, end_date
        )

        # Query the contribution of each category to the user's total income
        income_totals = calculate_income_totals(current_user.id, start_date, end_date)

        '''
        Include debt as a category that brings in Income
        '''
        # Query unique debtor names for the current user
        debtor_names = (
            db.session.query(Credit.debtor)
            .filter_by(user_id=current_user.id)
            .distinct()
            .all()
        )

        # Extract the debtor names from the query result and Populate the debtor field
        unique_debtors = [debtor[0] for debtor in debtor_names]

        # Calculate the sum of amount_payed for each debtor
        debtor_totals = {}
        for debtor_name in unique_debtors:
            total_amount_payed = (
                db.session.query(db.func.sum(Credit.amount_payed))
                .filter_by(user_id=current_user.id, debtor=debtor_name)
                .scalar()
            )
            if total_amount_payed is None:
                total_amount_payed = 0
            debtor_totals[debtor_name] = total_amount_payed

        # Calculate the sum of all amount_payed values in the debtor_totals dictionary
        total_debt_amount = sum(debtor_totals.values())

        # Add the total_debt_amount to the income_totals dictionary with 'Debt' as the key
        income_totals['Debt'] = total_debt_amount
    

        # Initialize a dictionary to store formatted amounts and percentages
        formatted_income_totals = {}

        # Calculate the total income
        total_income = sum(income_totals.values())

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


        response_data = {
            'total_income': str(total_income),  # Convert Decimal to string
            'individual_incomes': individual_incomes,
            'income_totals': income_totals
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Expense Magement ------------------------------------------------------------------------
@app.route('/expense', methods=['GET', 'POST'])
@login_required
def expense():
    if request.method == 'GET':

        # Query Income categories for the current user and Populate the incomeCategory field
        expense_categories = Expense.query.filter_by(user_id=current_user.id).all()
        expense_categories.insert(0, Expense(id=1, user_id=0, name='Credit'))

        # Query the contribution of each category to the user's total expense
        expense_totals = calculate_expense_totals(current_user.id)

        '''
        Include credit as a category that takes out Income
        '''
        # Query unique creditor names for the current user
        creditor_names = (
            db.session.query(Debt.creditor)
            .filter_by(user_id=current_user.id)
            .distinct()
            .all()
        )

        # Extract the debtor names from the query result
        unique_creditors = [debtor[0] for debtor in creditor_names]

        # Calculate the sum of amount_payed to each creditor
        creditor_totals = {}
        for creditor_name in unique_creditors:
            total_amount_payed = (
                db.session.query(db.func.sum(Debt.amount_payed))
                .filter_by(user_id=current_user.id, creditor=creditor_name)
                .scalar()
            )
            if total_amount_payed is None:
                total_amount_payed = 0
            creditor_totals[creditor_name] = total_amount_payed

        # Calculate the sum of all amount_payed values in the creditor_totals dictionary
        total_debt_amount = sum(creditor_totals.values())

        # Add the total_credit_amount to the expense_totals dictionary with 'Credit' as the key
        expense_totals['Credit'] = total_debt_amount
    

        # Initialize a dictionary to store formatted amounts and percentages
        formatted_expense_totals = {}

        # Calculate the total income
        total_expense = sum(expense_totals.values())

        # Format the amount values and update the income_totals dictionary
        for category, amount in expense_totals.items():
            formatted_amount = "{:,.2f}/=".format(amount)
            try:
                percentage = "{:.2f}".format((amount / total_expense) * 100)
            except ZeroDivisionError:
                percentage = "{:.2f}".format(0)
            formatted_expense_totals[category] = (formatted_amount, percentage)

        # Replace the original income_totals dictionary with the formatted one
        expense_totals = formatted_expense_totals

        print(expense_totals)

        # Call the calculate_total_income_between_dates function
        total_expenses, individual_expenses = calculate_total_expenses_between_dates(current_user.id)

        # Prepare the data in the desired format
        expense_transactions = [
            {
                'transaction_id': exp['id'],
                'expense_category_name': exp['name'],
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

        print(expense_transactions)
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
            print(category_name)

            user_id = current_user.id

            # Find the expense category ID for the given category name and current user
            if   category_name == 'Credit':
                expense_category = Expense.query.filter_by(user_id=0, name=category_name).first()
                print(expense_category)
            else:
                expense_category = Expense.query.filter_by(user_id=user_id, name=category_name).first()

            if expense_category:
                if category_name == 'Credit':
                    expense_category_id = 1

                else:
                    expense_category_id = expense_category.id

                print(expense_category_id)

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

# Create an expense transaction
@login_required
@app.route('/create_expense_transaction', methods=['POST'])
def create_expense_transaction():
    # Get form data from the request
    expense_category = request.form.get('expenseCategory')
    amount = request.form.get('amount')
    date = request.form.get('date')
    creditor = request.form.get('creditor')
    description = request.form.get('description')

    print(expense_category, amount, date, creditor, description)

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

        # Query the Debt model to find the appropriate debt using creditor and user_id
        debt_to_settle = Debt.query.filter_by(creditor=creditor, user_id=user_id, is_paid=False).first()

        if not debt_to_settle and expense_category == 1:
            raise ValueError("No outstanding credit found for the specified debtor.")


        # Call the add_cash_in_transaction function with the settled_credit_id
        cash_out = add_cash_out_transaction(
            user_id=user_id,
            amount=amount,
            date=date_obj,
            expense_id=expense_category,
            description=description,
            settled_debt_id=debt_to_settle.id if debt_to_settle else None
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
        # Query unique creditor names for the current user
        creditor_names = (
            db.session.query(Debt.creditor)
            .filter_by(user_id=current_user.id)
            .distinct()
            .all()
        )

        # Extract the creditor names from the query result
        unique_creditors = [creditor[0] for creditor in creditor_names]

        # Calculate the sum of amount_payed to each creditor
        creditor_totals = {}
        for creditor_name in unique_creditors:
            total_amount_payed = (
                db.session.query(db.func.sum(Debt.amount_payed))
                .filter_by(user_id=current_user.id, creditor=creditor_name)
                .scalar()
            )
            if total_amount_payed is None:
                total_amount_payed = 0
            creditor_totals[creditor_name] = total_amount_payed

        # Calculate the sum of all amount_payed values in the creditor_totals dictionary
        total_credit_amount = sum(creditor_totals.values())

        # Add the total_credit_amount to the expense_totals dictionary with 'Credit' as the key
        expense_totals['Credit'] = total_credit_amount
    

        # Initialize a dictionary to store formatted amounts and percentages
        formatted_expense_totals = {}

        # Calculate the total income
        total_expense = sum(expense_totals.values())

        # Format the amount values and update the expense_totals dictionary
        for category, amount in expense_totals.items():
            formatted_amount = "{:,.2f}/=".format(amount)
            try:
                percentage = "{:.2f}".format((amount / total_expense) * 100)
            except ZeroDivisionError:
                percentage = "{:.2f}".format(0)
            formatted_expense_totals[category] = (formatted_amount, percentage)

        # Replace the original expense_totals dictionary with the formatted one
        expense_totals = formatted_expense_totals


        print(total_expense)
        print(individual_expenses)
        print(expense_totals)
        response_data = {
            'total_expense': str(total_expense),
            'individual_expenses': individual_expenses,
            'expense_totals': expense_totals
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/manage_expense_transaction/<int:transaction_id>', methods=['PUT', 'DELETE'])
@login_required
def manage_cash_out_transaction(transaction_id):
    cash_out_transaction = CashOut.query.get(transaction_id)
    #print(cash_in_transaction, 'test 1')

    if not cash_out_transaction:
        return jsonify({'error': 'Transaction not found'}), 404

    print('test 2: transaction available')
    if request.method == 'PUT':
        try:
            # Get the data from the request JSON
            data = request.get_json()
            print(data, 'test 3 json data exists')
            # Validate and extract the data
            new_description = data.get('description', cash_out_transaction.description)
            print(new_description, 'test 4 new description check')

            new_amount = data.get('amount', cash_out_transaction.amount)
            print(new_amount, 'test 5 new amount check')

            new_date = data.get('date', cash_out_transaction.date)
            print(new_date, 'test 6 new date check')

            # Convert amount to appropriate data types (e.g., int, float)
            try:
                new_amount = float(new_amount)
                print(new_amount, 'test 7 new amount data type check')
            except ValueError:
                return jsonify({'error': 'Invalid data provided'}), 400
            
            # Convert the date string to a Python date object
            try:
                new_date = datetime.strptime(new_date, '%Y-%m-%d').date()
                print(new_description, 'test 8 new date data type check')
            except ValueError:
                return jsonify({'error': 'Invalid date provided'}), 400

            if new_amount < 0:
                print(new_amount, 'test 9 new amount less 0 check')
                return jsonify({'error': 'Amount cannot be negative'}), 400

            # Check if it's a credit given out 
            if cash_out_transaction.settled_debt_id is not None:
                print(new_description, 'test 10 this is a credit payment check')
                # Retrieve the associated debt object
                debt = Debt.query.get(cash_out_transaction.settled_debt_id)

                if debt is None:
                    #print(credit, 'test 11 new credit to be settled is available check')
                    return jsonify({'error': 'Associated debt not found'}), 400

                # Check if the credit has been settled
                if debt.is_paid:
                    #print(debt.is_paid, 'test 12 has the credit been paid already? check')
                    return jsonify({'error': 'Credit has already been paid'}), 400

                # Check if the new amount + amount_payed exceeds the debt amount
                if new_amount + debt.amount_payed > debt.amount:
                    print('test 13 Payment exceeds credit amount check')
                    return jsonify({'error': 'Payment exceeds credit amount'}), 400

                # Update the amount_payed field of the credit
                debt.amount_payed += new_amount

                # Mark the credit as paid if the amount_payed equals the credit amount
                if debt.amount_payed == debt.amount:
                    debt.is_paid = True

            # Call the update_transaction method
            cash_out_transaction.update_transaction(new_description, new_amount, new_date)

            # Format the date as 'yyyy-mm-dd'
            formatted_date = cash_out_transaction.date.strftime('%Y-%m-%d')

            # Create a dictionary with the updated data
            updated_data = {
                'message': 'Transaction updated successfully',
                'id': cash_out_transaction.id,
                'description': cash_out_transaction.description,
                'amount': cash_out_transaction.amount,
                'date': formatted_date,
            }

            return jsonify({'data': updated_data})

        except Exception as e:
            print('test 14 something else is wrong')
            return jsonify({'error': 'Invalid data format'}), 400

    elif request.method == 'DELETE':
        # Call the delete_transaction method
        cash_out_transaction.delete_transaction()
        return jsonify({'message': 'Transaction deleted successfully'})



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        initialize_default_income_types()

    app.run(debug=True)


