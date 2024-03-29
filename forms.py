from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, DateField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp

class RegistrationForm(FlaskForm):
    """
    Represents a registration form.
    
    Attributes:
        first_name (StringField): Field for entering the first name.
        last_name (StringField): Field for entering the last name.
        email (StringField): Field for entering an email address.
        password (PasswordField): Field for entering a password.
        confirm_password (PasswordField): Field for confirming the password.
        submit (SubmitField): Button for submitting the form.
    """
    
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50), Regexp('^[A-Za-z]*$', message='Only alphabetic characters are allowed.')],
                             render_kw={"autocomplete": "off", "class": "form-control", "placeholder": "John", "aria-label": "First name"})
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50), Regexp('^[A-Za-z]*$', message='Only alphabetic characters are allowed.')],
                            render_kw={"autocomplete": "off", "class": "form-control", "placeholder": "Doe", "aria-label": "Last name"})
    email = StringField('Email', validators=[DataRequired(), Email()],
                        render_kw={"autocomplete": "off", "class": "form-control", "placeholder": "johndoe@example.com", "aria-label": "Email"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8), Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]*$', message='Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character.')],
                             render_kw={"autocomplete": "off", "class": "form-control", "placeholder": "Password", "aria-label": "Password"})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')],
                                     render_kw={"autocomplete": "off", "class": "form-control", "placeholder": "Confirm password", "aria-label": "Confirm password"})
    submit = SubmitField('Sign Up', render_kw={"class": "btn btn-primary", "id": "registration-submit-button"})

class LoginForm(FlaskForm):
    """
    Represents a login form.
    
    Attributes:
        email (StringField): Field for entering an email address.
        password (PasswordField): Field for entering a password.
        submit (SubmitField): Button for submitting the form.
    """
    
    email = StringField('Email', validators=[DataRequired(), Email()],
                        render_kw={"autocomplete": "off", "class": "form-control", "placeholder": "johndoe@example.com", "aria-label": "Email"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8), Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]*$', message='Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character.')],
                             render_kw={"autocomplete": "off", "class": "form-control", "placeholder": "Password", "aria-label": "Password"})
    submit = SubmitField('Log In', render_kw={"class": "btn btn-primary", "id": "registration-submit-button"})

class IncomeCategoryForm(FlaskForm):
    """
    Represents a form for adding an income category.

    Attributes:
        categoryName (StringField): Field for entering the category name.
        incomeType (SelectField): Dropdown for choosing an income type.
    """
    
    categoryName = StringField('Category Name', validators=[DataRequired()])
    incomeType = SelectField('Choose Income Type', coerce=int)

class IncomeTransactionForm(FlaskForm):
    """
    Represents a form for adding an income transaction.

    Attributes:
        incomeCategory (SelectField): Dropdown for choosing a category.
        amount (FloatField): Field for entering the transaction amount.
        date (DateField): Field for entering the transaction date.
        debtor (SelectField): Dropdown for choosing a debtor (optional).
        description (TextAreaField): Field for entering a transaction description (optional).
    """
    
    incomeCategory = SelectField('Choose Category', coerce=int)
    amount = FloatField('Amount', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    debtor = SelectField('Debtor (optional)')
    description = TextAreaField('Description (optional)')
