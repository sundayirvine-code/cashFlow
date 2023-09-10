// Function to show a modal by ID
function showModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.style.display = 'block';
  }
}

// Function to hide a modal by ID
function hideModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.style.display = 'none';
  }
}

// Function to display a success message
function displaySuccessMessage(message) {
  const successMessage = document.getElementById('successMessage');
  if (successMessage) {
    successMessage.textContent = message;
    successMessage.style.display = 'block';
    successMessage.style.opacity = '1';

    setTimeout(() => {
      successMessage.style.opacity = '0';
      setTimeout(() => {
        successMessage.style.display = 'none';
      }, 500);
    }, 2000);
  }
}

// Function to handle the transaction action based on the query parameter
function handleTransactionAction(transactionId, action, newDescription, newAmount, newDate) {
  // Determine the URL based on the action
  const url = `/manage_income_transaction/${transactionId}?action=${action}`;

  // Prepare the request options based on the action
  const requestOptions = {
    method: action === 'edit' ? 'PUT' : 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
    body: action === 'edit' ? JSON.stringify({ description: newDescription, amount: newAmount, date: newDate }) : undefined,
  };

  // Make an AJAX request with the appropriate HTTP method and request options
  fetch(url, requestOptions)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Error: ${response.status} - ${response.statusText}`);
      }
      return response.json();
    })
    .then((data) => {
      if (action === 'edit') {
        // Handle editing success
        const editIcon = document.querySelector(`[data-transaction-id="${transactionId}"]`);
        const actionsCell = editIcon.parentElement;
        const amountCell = actionsCell.previousElementSibling;
        const dateCell = amountCell.previousElementSibling;
        const descriptionCell = dateCell.previousElementSibling;

        amountCell.textContent = data.data.amount;
        dateCell.textContent = data.data.date;
        descriptionCell.textContent = data.data.description;

        // Update the clicked icon's dataset elements
        editIcon.dataset.amount = data.data.amount;
        editIcon.dataset.description = data.data.description;
        editIcon.dataset.date = data.data.date;

        hideModal('modal-edit');
        displaySuccessMessage('Transaction Edited successfully');
      } else if (action === 'delete') {
        // Handle deletion success
        hideModal('modal-delete');
        displaySuccessMessage('Transaction Deleted successfully');

        // You can remove the corresponding row from the table if needed
        const tableBody = document.getElementById('transactionTableBody');
        const editIcon = document.querySelector(`[data-transaction-id="${transactionId}"]`);
        const tableRow = editIcon.parentElement.parentElement;

        // Add the 'fadeOut' class to initiate the animation
        tableRow.classList.add('fadeOut');

        // Wait for the animation to complete
        setTimeout(() => {
          tableRow.classList.remove('fadeOut');
          tableBody.removeChild(tableRow);
        }, 900); // Adjust the delay to match the animation duration
      }
    })
    .catch((error) => {
      console.error(`Error ${action}ing transaction:`, error);
    });
}

// Function to initialize the event listeners
function initializeEventListeners() {
  const transactionTableBody = document.getElementById('transactionTableBody');

  transactionTableBody.addEventListener('click', (event) => {
    const target = event.target;

    if (target.classList.contains('edit-transaction')) {
      const transactionId = target.dataset.transactionId;
      const description = target.dataset.description;
      const amount = target.dataset.amount;
      const date = target.dataset.date;

      document.getElementById('Editamount').value = amount;
      document.getElementById('Editdate').value = date;
      document.getElementById('Editdescription').value = description;

      showModal('modal-edit');

      document.getElementById('submitEditTransactionForm').addEventListener('click', () => {
        const newDescription = document.getElementById('Editdescription').value;
        const newAmount = parseFloat(document.getElementById('Editamount').value);
        const newDate = document.getElementById('Editdate').value;

        if (!(newAmount) || newAmount < 0) {
          alert('Please enter a valid positive amount.');
          return;
        }
        const currentDate = new Date();
        const entereddate = new Date(newDate);
        if (entereddate > currentDate) {
          alert('Please select a date that is not in the future.');
          return;
        }

        if (newDescription.length > 100) {
          alert('Description should not exceed 100 characters.');
          return;
        }

        handleTransactionAction(transactionId, 'edit', newDescription, newAmount, newDate);
      });
    }

    if (target.classList.contains('delete-transaction')) {
      const transactionId = target.dataset.transactionId;
      showModal('modal-delete');

      document.getElementById('modal-content-delete').addEventListener('click', () => {
        handleTransactionAction(transactionId, 'delete');
      });
    }
  });

  document.getElementById('cancelEditTransaction').addEventListener('click', () => {
    hideModal('modal-edit');
  });

  document.getElementById('modal-content-cancel').addEventListener('click', () => {
    hideModal('modal-delete');
  });
}

// Add an event listener to the window load event
window.addEventListener('load', initializeEventListeners);
