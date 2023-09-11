// Function to fetch chart data and render the chart
async function renderChart() {
    try {
        // Fetch chart data from the '/chart_data' route
        const response = await fetch('/chart_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error('Failed to fetch chart data');
        }

        const chartData = await response.json();

        // Get the chart container elements
        const incomechartContainer = document.getElementById('incomeChart');
        const chartContainer = document.getElementById('expenseChart');

        // Create a canvas element to render the chart
        const canvas = document.createElement('canvas');
        chartContainer.appendChild(canvas);

        const incomecanvas = document.createElement('canvas');
        incomechartContainer.appendChild(incomecanvas);

        const ctx = canvas.getContext('2d');
        const incomectx = incomecanvas.getContext('2d');

        // Create and configure the chart using Chart.js
        const incomechart = new Chart(incomectx, {
            type: 'doughnut',
            data: {
                labels: chartData.income_chart_data.labels,
                datasets: [{
                    label: 'Income',
                    data: chartData.income_chart_data.values,
                    backgroundColor: chartData.expense_chart_data.colors,
                    borderColor: '#d4d9d6',  // Set border color for pie chart slices
                    borderWidth: 1,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,  // Allow chart resizing
                devicePixelRatio: 2,  // Increase the pixel ratio as needed
                plugins: {
                    legend: {
                        position: 'right',  // Move the legend to the right
                        labels: {
                            font: {
                                size: 12,  // Set legend label font size
                            },
                        },
                    },
                    title: {
                        display: true,
                        text: 'Income Breakdown', // Set your chart title here
                        font: {
                            size: 15, // Set the font size for the title
                            weight: 'bold', // Set the font weight (optional)
                        },
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                // Format the tooltip label as a percentage with a percent symbol
                                const value = context.parsed;
                                return value.toFixed(2) + '%'; // Two decimal places and a percent symbol
                            },
                        },
                    },
                },
            },
        });

        // Create and configure the chart using Chart.js
        const chart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: chartData.expense_chart_data.labels,
                datasets: [{
                    label: 'Expenses',
                    data: chartData.expense_chart_data.values,
                    backgroundColor: chartData.expense_chart_data.colors,
                    borderColor: '#d4d9d6',  // Set border color for pie chart slices
                    borderWidth: 1,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,  // Allow chart resizing
                devicePixelRatio: 2,  // Increase the pixel ratio as needed
                plugins: {
                    legend: {
                        position: 'right',  // Move the legend to the right
                        labels: {
                            font: {
                                size: 12,  // Set legend label font size
                            },
                        },
                    },
                    title: {
                        display: true,
                        text: 'Expense Breakdown', // Set your chart title here
                        font: {
                            size: 15, // Set the font size for the title
                            weight: 'bold', // Set the font weight (optional)
                        },
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                // Format the tooltip label as a percentage with a percent symbol
                                const value = context.parsed;
                                return value.toFixed(2) + '%'; // Two decimal places and a percent symbol
                            },
                        },
                    },
                },
            },
        });

    } catch (error) {
        console.error('Error fetching chart data:', error);
    }
}

Chart.defaults.color = 'white';
// Call the function when the page loads
window.onload = renderChart;
