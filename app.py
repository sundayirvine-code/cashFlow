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
 
    
    

