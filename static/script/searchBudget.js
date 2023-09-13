document.addEventListener("DOMContentLoaded", function() {
    // Populate year select options
    var currentYear = new Date().getFullYear();
    var yearSelect = document.getElementById('yearSelect');
    for (var year = currentYear; year >= currentYear - 20; year--) {
        var option = document.createElement('option');
        option.value = year;
        option.text = year;
        yearSelect.appendChild(option);
    }

    // Populate month select options
    var monthSelect = document.getElementById('monthSelect');
    var months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    for (var i = 0; i < months.length; i++) {
        var monthValue = (i + 1).toString().padStart(2, '0'); // Zero-padding for single-digit months
        var option = document.createElement('option');
        option.value = monthValue;
        option.text = months[i];
        monthSelect.appendChild(option);
    }

    document.getElementById('searchButton').addEventListener('click', function() {
        // Get selected year and month values
        var selectedYear = yearSelect.value;
        var selectedMonth = monthSelect.value;

        // Perform your asynchronous search using these values
        // You can make an AJAX request or perform any other action here
        // For example:
        console.log("Searching for budget with Year: " + selectedYear + " and Month: " + selectedMonth);
    });
});