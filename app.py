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
        return abort(405)  # Method Not Allowed
 
    

