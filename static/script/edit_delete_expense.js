// Function to open the edit modal and populate it with data
function openEditModal(transactionId, description, amount, date) {
    const editModal = document.getElementById('modal-edit');
    const editDescriptionInput = document.getElementById('Editdescription');
    const editAmountInput = document.getElementById('Editamount');
    const editDateInput = document.getElementById('Editdate');
  
    // Populate the input fields
    editDescriptionInput.value = description;
    editAmountInput.value = parseFloat(amount.replace(/,|\/=|\s/g, ''));
    editDateInput.value = date;
  
    // Show the edit modal
    editModal.style.display = 'block';
  
    // Add event listener to the submit button in the edit modal
    document.getElementById('submitEditTransactionForm').addEventListener('click', () => {
      // Get the updated values from the input fields
      const newDescription = editDescriptionInput.value;
      const newAmount = parseFloat(editAmountInput.value);
      const newDate = editDateInput.value;
  
      // Validate the input values
      if (!(newAmount) || newAmount < 0) {
        alert('Please enter a valid positive amount.');
        return;
      }
      const currentDate = new Date();
      const enteredDate = new Date(newDate);
      if (enteredDate > currentDate) {
        alert('Please select a date that is not in the future.');
        return;
      }
      if (newDescription.length > 100) {
        alert('Description should not exceed 100 characters.');
        return;
      }
  
      // Call the function to handle the transaction action (edit)
      handleTransactionAction(transactionId, 'edit', newDescription, newAmount, newDate);
    });
  }
  
  // Function to open the delete modal
  function openDeleteModal(transactionId) {
    const deleteModal = document.getElementById('modal-delete');
    deleteModal.style.display = 'block';
  
    // Add event listener to the submit button in the delete modal
    document.getElementById('modal-content-delete').addEventListener('click', () => {
      // Call the function to handle the transaction action (delete)
      handleTransactionAction(transactionId, 'delete');
    });
  }
  
  // Function to handle the transaction action (edit or delete)
  function handleTransactionAction(transactionId, action, newDescription, newAmount, newDate) {
    // Construct the URL based on the action
    const url = `/manage_expense_transaction/${transactionId}?action=${action}`;
  
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
          // Update the table row with the edited data here
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
  
          // Hide the edit modal
          document.getElementById('modal-edit').style.display = 'none';
  
          // Display a success message (similar to your original code)
          displaySuccessMessage('Transaction Edited successfully');
        } else if (action === 'delete') {
          // Handle deletion success
          // Remove the corresponding row from the table here
          const tableBody = document.getElementById('transactionTableBody');
          const editIcon = document.querySelector(`[data-transaction-id="${transactionId}"]`);
          const tableRow = editIcon.parentElement.parentElement;

          // Add the 'fadeOut' class to initiate the animation
         tableRow.classList.add('fadeOut');

         // Wait for the animation to complete (0.5s in this example)
         setTimeout(() => {
             // Remove the 'fadeOut' class and then remove the table row from the DOM
             tableRow.classList.remove('fadeOut');
             tableBody.removeChild(tableRow);
         }, 900); // Adjust the delay to match the animation duration
  
          // Hide the delete modal
          document.getElementById('modal-delete').style.display = 'none';
  
          // Display a success message
          displaySuccessMessage('Transaction Deleted successfully');
        }
      })
      .catch((error) => {
        console.error(`Error ${action}ing transaction:`, error);
      });
  }
  
  // Function to display a success message
  function displaySuccessMessage(message) {
    const successMessage = document.getElementById('successMessage');
    successMessage.textContent = message;
    successMessage.style.display = 'block';
    successMessage.style.opacity = '1';
  
    // Use setTimeout to hide the message after a delay
    setTimeout(() => {
      // Set the opacity to 0 for fading out
      successMessage.style.opacity = '0';
  
      // After the transition completes (0.5 seconds), hide the message
      setTimeout(() => {
        successMessage.style.display = 'none';
      }, 500);
    }, 2000);
  }
  
  // Add event listener to the table body for click events (event delegation)
  document.getElementById('transactionTableBody').addEventListener('click', (event) => {
    const target = event.target;
  
    // Check if the clicked element is an edit icon
    if (target.classList.contains('edit-transaction')) {
      const transactionId = target.dataset.transactionId;
      const description = target.dataset.description;
      const amount = target.dataset.amount;
      const date = target.dataset.date;
      
      openEditModal(transactionId, description, amount, date);
    }
  
    // Check if the clicked element is a delete icon
    if (target.classList.contains('delete-transaction')) {
      const transactionId = target.dataset.transactionId;
      openDeleteModal(transactionId);
    }
  });
  
  // Add event listener to cancel buttons in both modals to hide them
  document.getElementById('cancelEditTransaction').addEventListener('click', () => {
    document.getElementById('modal-edit').style.display = 'none';
  });
  
  document.getElementById('modal-content-cancel').addEventListener('click', () => {
    document.getElementById('modal-delete').style.display = 'none';
  });
  