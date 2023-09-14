
// Attach click event listener to budget cards
const budgetCards = document.querySelectorAll('.budgetcard');
budgetCards.forEach(card => {
    card.addEventListener('click', () => {
        // Retrieve the budget ID from the dataset attribute
        const budgetId = card.dataset.budgetId;

        console.log(budgetId);

        // Send an asynchronous request to the server
        fetch(`/search_budget_expenses/${budgetId}`)
            .then(response => response.json())
            .then(data => {
                // Populate the table with retrieved data
                populateTableWithData(data);
            })
            .catch(error => {
                console.error('Error searching budget expenses:', error);
            });
    });
});

// Function to populate the table with data
function populateTableWithData(data) {
    // Clear the existing table rows
    const tableBody = document.getElementById('transactionTableBody');
    tableBody.innerHTML = '';

    // Loop through the data and create table rows
    data.budget_expenses.forEach(expense => {
        const newRow = document.createElement('tr');
        newRow.setAttribute('data-row-id', expense.id);
        

        newRow.innerHTML = `
            <td>${expense.expense_name}</td>
            <td style="color: #bfd220;">${expense.expected_amount}</td>
            <td style="color:${expense.expected_amount >= expense.spent_amount ? '#bfd220' : '#f95395'};">${expense.spent_amount}</td>
            <td>${expense.percentage}%</td>
            <td class="actions">
                <!-- Edit and Delete buttons with appropriate data attributes -->
                <i class="fas fa-edit edit-transaction"
                data-budgetexpense-id="${expense.id}"
                data-budget-id="${expense.budget_id}"
                data-estimate="${expense.expected_amount}"
                data-expensename="${expense.expense_name}"
                data-expenseid="${expense.expense_id}"
                aria-hidden="true"></i>
                <i class="fas fa-trash-alt delete-transaction"
                data-budgetexpense-id="${expense.id}"
                aria-hidden="true"></i>
            </td>
        `;

        console.log(newRow);
        
        tableBody.appendChild(newRow);
    });
}
