function createBudget() {
    fetch('/budget', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        // Handle the response, e.g., display a success message
        console.log('Budget created:', data);

        // Map month numbers to their names
        const monthNames = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ];

        // Get the month name based on the month number
        const monthName = monthNames[data.month - 1];

        // Update the <h4> element with the received JSON data
        const currentBudgetElement = document.getElementById('currentBudgetInfo');
        if (currentBudgetElement) {
            currentBudgetElement.textContent = `${data.month} ${monthName}`;
        }

        // Create a new budget card
        const previousBudgetsContainer = document.getElementById('previousBudgets');
        if (previousBudgetsContainer) {
            const newBudgetCard = document.createElement('div');
            newBudgetCard.classList.add('budgetcard');
            newBudgetCard.setAttribute('data-budget-id', data.id);

            // Populate the new budget card with data
            newBudgetCard.innerHTML = `
                <h4>${monthName} ${data.year}</h4>
                <p>Estimate: ${data.expected_amount || '0.00'}</p>
                <p>Actual: ${data.spent_amount || '0.00'}</p>
            `;

            // Append the new budget card as the first child of the container
            previousBudgetsContainer.insertBefore(newBudgetCard, previousBudgetsContainer.firstChild);

            // Display the success message
            successMessage=document.getElementById('successMessage');
            successMessage.textContent = 'Budget created successfully';
            successMessage.style.display = 'block';
            successMessage.style.opacity = '1'; 

            // Use setTimeout to hide the message after a delay
            setTimeout(() => {
                successMessage.style.opacity = '0';
                setTimeout(() => {
                    successMessage.style.display = 'none';
                }, 500);
            }, 2000);
        }

        const addBudgetExpensesBtn = document.getElementById('addBudgetExpenses');
        if(addBudgetExpensesBtn){
            addBudgetExpensesBtn.style.display='inline';              
        }
        document.getElementById('createBudget').style.display='none'; 
    })
    .catch(error => {
        // Handle errors
        console.error('Error creating budget:', error);
        // Display the error message
        errorMessage=document.getElementById('errorMessage');
        errorMessage.textContent = 'Error creating budget: ${error}';
        errorMessage.style.display = 'block';
        errorMessage.style.opacity = '1'; 

        // Use setTimeout to hide the message after a delay
        setTimeout(() => {
            errorMessage.style.opacity = '0';
            setTimeout(() => {
                errorMessage.style.display = 'none';
            }, 500);
        }, 2000);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Attach the click event listener to the createBudget icon
    const createBudgetIcon = document.getElementById('createBudget');
    if (createBudgetIcon) {
        createBudgetIcon.addEventListener('click', createBudget);
    }
});
