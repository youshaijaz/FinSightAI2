// FinSight AI Chart.js Configurations

// Pie Chart for Spending by Category
function initializePieChart(labels, data) {
    const ctx = document.getElementById('pieChart').getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: ['#ff6384', '#36a2eb', '#ffce56', '#4bc0c0'],
                borderColor: '#fff',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'top' },
                title: {
                    display: true,
                    text: 'Spending by Category'
                }
            }
        }
    });
}

// Placeholder for Line Chart (Expenses Over Time)
// function initializeLineChart(labels, data) {
//     const ctx = document.getElementById('lineChart').getContext('2d');
//     new Chart(ctx, {
//         type: 'line',
//         data: {
//             labels: labels, // e.g., ['2025-10-01', '2025-10-02', ...]
//             datasets: [{
//                 label: 'Expenses',
//                 data: data, // e.g., [50, 500, 100, ...]
//                 borderColor: '#36a2eb',
//                 fill: false,
//                 tension: 0.1
//             }]
//         },
//         options: {
//             responsive: true,
//             plugins: {
//                 legend: { position: 'top' },
//                 title: {
//                     display: true,
//                     text: 'Expenses Over Time'
//                 }
//             },
//             scales: {
//                 x: { title: { display: true, text: 'Date' } },
//                 y: { title: { display: true, text: 'Amount ($)' } }
//             }
//         }
//     });
// }

// Initialize charts when the page loads
document.addEventListener('DOMContentLoaded', function () {
    // Get data from Django template (passed via data attributes or global variable)
    const pieChartElement = document.getElementById('pieChart');
    if (pieChartElement) {
        const labels = JSON.parse(pieChartElement.dataset.labels || '[]');
        const data = JSON.parse(pieChartElement.dataset.data || '[]');
        initializePieChart(labels, data);
    }


    const lineChartElement = document.getElementById('lineChart');
    if (lineChartElement) {

        const labels = JSON.parse(lineChartElement.dataset.labels || '[]');
        const data = JSON.parse(lineChartElement.dataset.data || '[]');
        initializeLineChart(labels, data);
    }
});