// Function to show a success message with custom colors
function showSuccessMessage(message) {
    const successMessage = document.getElementById('successMessage');
    successMessage.textContent = message;
    successMessage.style.backgroundColor = '#f95395';
    successMessage.style.color = 'black';
    successMessage.style.display = 'block';
    successMessage.style.opacity = '1';
  
    setTimeout(() => {
      successMessage.style.opacity = '0';
      setTimeout(() => {
        successMessage.style.display = 'none';
      }, 500);
    }, 2000);
  }
  
  // Function to create a category card element
  function createCategoryCard(category, amount, percentage) {
    const card = document.createElement('div');
    card.className = 'catCard';
    card.dataset.categoryname = category;
  
    const categoryNameElement = document.createElement('div');
    categoryNameElement.style.fontSize = '16px';
    categoryNameElement.style.fontWeight = '400';
    categoryNameElement.textContent = category;
  
    const amountElement = document.createElement('div');
    amountElement.style.color = '#bfd220';
    amountElement.style.fontWeight = '600';
    amountElement.style.fontSize = '27px';
    amountElement.textContent = amount;
  
    const percentageElement = document.createElement('div');
    percentageElement.style.fontSize = '12px';
    percentageElement.textContent = percentage + '%';
  
    const progressBarContainer = document.createElement('div');
    progressBarContainer.style.maxWidth = '150px';
    progressBarContainer.style.width = '150px';
    progressBarContainer.style.height = '4px';
    progressBarContainer.style.backgroundColor = 'white';
    progressBarContainer.style.paddingBottom = '3px';
  
    const progressBar = document.createElement('div');
    progressBar.style.backgroundColor = '#141c33';
    progressBar.style.height = '4px';
    progressBar.style.width = percentage + '%';
  
    progressBarContainer.appendChild(progressBar);
    card.appendChild(categoryNameElement);
    card.appendChild(amountElement);
    card.appendChild(percentageElement);
    card.appendChild(progressBarContainer);
  
    return card;
  }
  
  // Function to format a date as 'Month Day, Year'
  function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', options);
  }
  
  // Function to format income amount with commas and add '/='
  function formatIncome(amount) {
    return amount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',') + '/=';
  }
  
  // Function to update the summary section
  function updateSummary(data, fromDate, toDate) {
    const formattedIncome = formatIncome(data.total_income);
    document.getElementById('incomeSummaryAmount').textContent = formattedIncome;
    document.getElementById('fromincomeSummaryDateRange').textContent = formatDate(fromDate);
    document.getElementById('toincomeSummaryDateRange').textContent = formatDate(toDate);
  }
  
  // Function to update the transaction table
  function updateTransactionTable(transactions) {
    const tableBody = document.getElementById('transactionTableBody');
    tableBody.innerHTML = '';
  
    transactions.forEach((transaction) => {
      const formattedDate = new Date(transaction.date).toISOString().split('T')[0];
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${transaction.id}</td>
        <td>${transaction.name}</td>
        <td>${transaction.description}</td>
        <td>${formattedDate}</td>
        <td class="income_amount_cell">${transaction.amount}</td>
        <td class="actions">
          <i class="fas fa-edit edit-transaction" data-transaction-id="${transaction.id}" data-description="${transaction.description}" data-amount="${transaction.amount}" data-date="${formattedDate}"></i>
          <i class="fas fa-trash-alt delete-transaction" data-transaction-id="${transaction.id}"></i> 
        </td>
      `;
      tableBody.appendChild(row);
    });
  }
  
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.catCard').forEach(function (card) {
      card.addEventListener('click', function () {
        var category_name = this.getAttribute('data-categoryname');
  
        console.log(category_name);
  
        fetch('/income', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ category_name: category_name }),
        })
          .then(response => {
            if (!response.ok) {
              throw new Error('Network response was not ok');
            }
            return response.json();
          })
          .then(data => {
            console.log(data.transactions);
            updateSummary(data, fromInput.value, toInput.value);
            updateTransactionTable(data.individual_incomes);
          })
          .catch(error => {
            console.error(error.message);
          });
      });
    });
  
    const fromInput = document.getElementById('dateRangePickerFrom');
    const toInput = document.getElementById('dateRangePickerTo');
    const searchButton = document.getElementById('searchButton');
  
    searchButton.addEventListener('click', function () {
      const fromDate = fromInput.value;
      const toDate = toInput.value;
  
      console.log(fromDate, toDate);
  
      if (!fromDate || !toDate) {
        alert('Please select both "From" and "To" dates.');
        return;
      }
  
      const currentDate = new Date().toISOString().split('T')[0];
  
      if (fromDate > toDate) {
        alert('"From" date should not be greater than "To" date.');
        return;
      }
  
      if (fromDate > currentDate || toDate > currentDate) {
        alert('Selected dates should not be in the future.');
        return;
      }
  
      const url = `/search_income_transactions?from=${fromDate}&to=${toDate}`;
  
      fetch(url)
        .then(response => response.json())
        .then(data => {
          console.log('Search results:', data);
          if (data.individual_incomes.length === 0) {
            showSuccessMessage('No existing transactions in that date period');
          }
          updateTransactionTable(data.individual_incomes);
          updateSummary(data, fromDate, toDate);
        })
        .catch(error => {
          console.error('Error searching transactions:', error);
        });
    });
  });
  