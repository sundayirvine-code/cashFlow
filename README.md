# cashflow

![CashFlow](/static/designs/landing.png)

## Introduction
CashFlow is a comprehensive personal financial tracking system designed to empower individuals to manage their finances effectively and gain better control over their spending habits.
The system provides real-time visibility into Expenditure, Incomes, and Credit, Debt, Budget, all including data visualization using charts enabling individuals to make informed decisions and minimize waste.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Technologies Used](#technologies-used)
- [Configuration](#configuration)
- [Roadmap](#roadmap)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Acknowledgements](#acknowledgements)
- [Contact Information](#contact-information)

## Installation
To install CashFlow on your local development environment, follow these steps:

1. Clone the repository from GitHub:   
```bash
git clone https://github.com/sundayirvine-code/cashFlow.git
```
2. Install the required dependencies:  
```bash
pip install -r requirements.txt
```
3. Configure the environment variables:  
Edit the `.env` file and provide the necessary configuration if you are using a Mysql databse. Otherwise comment out the Mysql databse configuration on the `app.py` file like so and use sqlite as the databse.:  
```python
#app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
```  
4. Start the CashFlow server: 
```python
python app.py
```  

## Usage
CashFlow provides a user-friendly interface to manage and explore incomes and expenses. Here are some examples of how to use CashFlow:

1. **Sign up:**
   - Navigate to the CashFlow landing page.
   - Click on the "Sign Up" link.
   - Fill out the required information to create a new account.

2. **Log in:**
   - After signing up, you will be directed to the login page.
   - Enter your credentials (email and password) to access your account.

3. **Manage Income:**
   - Locate the 'Income' tab on the navigation menu and click on it. You will be directed to the income management page.
   - First create income categories by clicking the "+" button in the categories section.
   - create an Income transaction entry by clicking the "+" button in the transactions section. Fill the required details and submit

4.  **Manage Expense:**
   - Locate the 'Expense' tab on the navigation menu and click on it. You will be directed to the expense management page.
   - First create expense categories by clicking the "+" button in the categories section.
   - create an Expense transaction entry by clicking the "+" button in the transactions section. Fill the required details and submit

5.  **Manage Credit:**
   - This is the section that helps you manage the way you lend your money
   - Locate the 'Credit' tab on the navigation menu and click on it. You will be directed to the Credit management page.
   - create a Credit transaction entry by clicking the "+" button in the debtors section. Fill the required details and submit

6. **Manage Debt:**
   - This is the section that helps you manage the way you borrow your money
   - Locate the 'Debt' tab on the navigation menu and click on it. You will be directed to the Debt management page.
   - create a Debt transaction entry by clicking the "+" button in the creditors section. Fill the required details and submit

7. **Manage Budget:**
   - This is the section that helps you manage your monthly budget
   - Locate the 'Budget' tab on the navigation menu and click on it. You will be directed to the Budget management page.
   - First create the current month's budget by clicking the "+" button in the prev budgets section.
   - Include expenses you want to track in your budget and the extimate amount by clicking the  "+" button in the current month's budget section.
   - Refresh the page to see current expenses included.
   

8. **View Analytics:**
   - To be developed


## Technologies Used

This project was developed using the following technologies:

- **HTML:** The standard markup language for creating the structure and content of web pages. [Learn more](https://developer.mozilla.org/en-US/docs/Web/HTML)

- **CSS:** A stylesheet language used for describing the presentation of a document written in HTML. [Learn more](https://developer.mozilla.org/en-US/docs/Web/CSS)

- **Bootstrap:** A popular CSS framework that provides pre-designed responsive components and styles to simplify web development. [Learn more](https://getbootstrap.com/)

- **Python:** A versatile and powerful programming language used for server-side development, data processing, and automation. [Learn more](https://www.python.org/)

- **JavaScript:** A programming language that enables dynamic and interactive behavior on web pages. [Learn more](https://developer.mozilla.org/en-US/docs/Web/JavaScript)

- **jQuery:** A fast and concise JavaScript library that simplifies HTML document traversal, event handling, and animation. [Learn more](https://jquery.com/)

- **Flexbox:** A CSS layout module that provides a flexible way to distribute and align elements within a container. [Learn more](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Flexible_Box_Layout)

- **CSS Grid:** A powerful two-dimensional layout system in CSS that allows for the creation of complex grid-based layouts. [Learn more](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout)


## Configuration

To configure the project and connect it to your database, follow these steps:

1. Open the `.env` file in the project directory.

2. Locate the `DATABASE_URI` variable and replace its value with your unique database information.

   Example:
   ```python
   DATABASE_URI=mysql+pymysql://username:password@localhost:3306/mydatabase
   ```

Make sure to update the username, password, host, and database name based on your own configuration.

3. Save the changes to the `.env` file.

By updating the `DATABASE_URI` with your own database information, the project will be able to establish a connection and interact with your database accordingly.

Note: Ensure that you have the necessary database permissions and that the database is accessible from the environment where the project is running.  

## Roadmap
We have an exciting roadmap for CashFlow, with several upcoming features and enhancements planned. Here are some of the key milestones and future plans:

1. Enhanced User Interface: We are continuously working on improving the user interface to make it more intuitive and user-friendly. This includes refining the design, optimizing layouts, and adding new visual elements.

2. Mobile App Integration: We are planning to develop a mobile application for cashFlow, allowing users to manage their finances on-the-go. The mobile app will provide a seamless experience with all the features available in the web version.

3. Automation: We are planning to automate the entry of repetitive expenses to allow the user easily enter a bunch of expenses in one click! Convenient right?

4. Integration with Mobile Money Platforms: We aim to integrate CashFlow with popular e-commerce platforms, such as M-Pesa or Airtel Money. This integration will allow users to synchronize their Income and Expenses with their E wallets.

5. Advanced Analytics: We will be expanding the analytics capabilities of CashFlow to provide more in-depth insights into expense trends, Incomes, cCredit, and Debt. Users will be able to generate detailed reports and visualize data using charts and graphs.

Stay tuned for these exciting updates as we continue to develop and enhance CashFlow to meet the needs of individuals who want to take a hold of their finances!

## Troubleshooting
Here are some common issues or errors that users may encounter while using CashFlow, along with their respective solutions or workarounds:

1. Database Connection Errors: If users encounter issues connecting to the database, they should verify that the database URI in the .env file is correctly configured with their unique database information. Make sure the username, password, host, and database name are accurate. If the issue persists, users can check their network connection and ensure that the database server is accessible.

2. Missing Dependencies: If users encounter missing dependencies or module import errors, it's recommended to verify that all the required dependencies are installed. They can run the command `pip install -r requirements.txt` to install the necessary packages specified in the project's requirements.txt file.

3. CSS or Styling Issues: If the user interface appears distorted or the styling is not being applied correctly, it could be due to caching or loading issues. In such cases, users can try clearing their browser cache or force-refresh the page (Ctrl + Shift + R or Cmd + Shift + R) to ensure the latest styles are loaded.

4. Authentication Problems: If users are unable to log in or access certain features, they should double-check their login credentials and ensure they are using the correct username and password. 

5. Performance, ServerError or Speed Issues: If CahsFlow is running slowly or experiencing performance issues, it could be due to the fact that I am currently hosting the page using the free version of PythonAnywhere that offers limited features. Users can try refreshing the page, closing unnecessary browser tabs, or reaching out to the support team if the problem persists.

## License
CashFlow is distributed under the MIT License.

The MIT License is a permissive open-source license that allows you to use, modify, and distribute the software, both commercially and non-commercially, as long as you include the original license in your distribution. It provides flexibility and freedom for developers to use CashFlow in their projects.
For more information about the MIT License, please visit opensource.org/licenses/MIT.

## Acknowledgements
We would like to express our gratitude to the following individuals, projects, and resources that have contributed to the development of CashFlow:

OpenAI: We would like to thank OpenAI for providing the underlying technology that powers ChatGPT, which has been instrumental in assisting us throughout the development process.

Bootstrap: We are grateful to the Bootstrap framework for its robust and responsive CSS and JavaScript components, which have greatly contributed to the overall design and user experience of CashFlow.

We also extend our gratitude to all the individuals, developers, and communities who have contributed to the open-source projects, libraries, and resources that we have utilized in the development of CashFlow. Your work and dedication have played a significant role in the success of this project.

## Contact Information
For any inquiries or feedback regarding CashFlow, you can reach out to the project maintainer, Irvine Sunday, using the following contact information:

GitHub: [sundayirvine-code](https://github.com/sundayirvine-code/)  
LinkedIn: [Irvine Sunday](https://www.linkedin.com/in/irvine-amugumbi-49ba6b201/)  
Portfolio: [Irvine Sunday's Portfolio](https://irvine-sunday-portfolio.vercel.app/)
CashFlow: [CashFlow](https://cashflow.pythonanywhere.com/)    
Feel free to connect with me through these platforms for any questions, suggestions, or collaboration opportunities. I look forward to hearing from you!
