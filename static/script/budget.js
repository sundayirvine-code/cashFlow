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

        const addBudgetExpensesBtn = document.getElementById('addBudgetExpenses');
        if(addBudgetExpensesBtn){
            addBudgetExpensesBtn.style.display='inline';              
        }
    })
    .catch(error => {
        // Handle errors
        console.error('Error creating budget:', error);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Attach the click event listener to the createBudget icon
    const createBudgetIcon = document.getElementById('createBudget');
    if (createBudgetIcon) {
        createBudgetIcon.addEventListener('click', createBudget);
    }
});
