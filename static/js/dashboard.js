document.addEventListener('DOMContentLoaded', function() {
    const profitMarginData = {
        labels: ['Total Spent', 'Amazon Commission', 'Profit Margin'],
        datasets: [{
            label: 'Profit Breakdown',
            data: [
                totalBuyPrice,
                totalAmazonCommission,
                totalProfit
            ],
            backgroundColor: ['#FF6384', '#36A2EB', '#4BC0C0'],
            hoverBackgroundColor: ['#FF6384', '#36A2EB', '#4BC0C0']
        }]
    };

    const ordersSummaryData = {
        labels: ['Received', 'Returned', 'Delivered', 'Shipped', 'Cancelled'],
        datasets: [{
            label: 'Orders',
            data: [
                receivedOrders,
                returnedOrders,
                deliveredOrders,
                shippedOrders,
                cancelledOrdersCount
            ],
            backgroundColor: ['#4BC0C0', '#FF6384', '#FFCE56', '#36A2EB', '#FF9F40'],
            hoverBackgroundColor: ['#4BC0C0', '#FF6384', '#FFCE56', '#36A2EB', '#FF9F40']
        }]
    };

    const salesValueData = {
        labels: salesValueDates,
        datasets: [{
            label: 'Sales Value',
            data: salesValueValues,
            borderColor: '#36A2EB',
            fill: false
        }]
    };

    const performanceData = {
        labels: performanceDates,
        datasets: [{
            label: 'Total Orders',
            data: performanceCounts,
            backgroundColor: '#FF6384',
            hoverBackgroundColor: '#FF6384'
        }]
    };

    const salesByRegionData = {
        labels: salesByRegionLabels,
        datasets: [{
            label: 'Sales by Region',
            data: salesByRegionValues,
            backgroundColor: ['#4BC0C0', '#FF6384', '#FFCE56', '#36A2EB'],
            hoverBackgroundColor: ['#4BC0C0', '#FF6384', '#FFCE56', '#36A2EB']
        }]
    };

    const salesBySupplierData = {
        labels: salesBySupplierLabels,
        datasets: [{
            label: 'Number of Orders',
            data: salesBySupplierCounts,
            backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'],
            hoverBackgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
        }]
    };

    new Chart(document.getElementById('profitMarginChart'), {
        type: 'pie',
        data: profitMarginData
    });

    new Chart(document.getElementById('ordersSummaryChart'), {
        type: 'bar',
        data: ordersSummaryData
    });

    new Chart(document.getElementById('salesValueChart'), {
        type: 'line',
        data: salesValueData
    });

    new Chart(document.getElementById('performanceChart'), {
        type: 'bar',
        data: performanceData
    });

    new Chart(document.getElementById('salesByRegionChart'), {
        type: 'bar',
        data: salesByRegionData
    });

    new Chart(document.getElementById('salesBySupplierChart'), {
        type: 'bar',
        data: salesBySupplierData
    });

    let currency = 'USD';
    let exchangeRate;
    
    async function fetchExchangeRate() {
        const response = await fetch('https://api.exchangerate-api.com/v4/latest/USD');
        const data = await response.json();
        exchangeRate = data.rates.INR;
    }
    
    function formatCurrency(value, targetCurrency) {
        value = parseFloat(value.replace(/[^\d.-]/g, '')); // Remove any existing currency symbols
        if (targetCurrency === 'USD') {
            return '$' + value.toFixed(2);
        } else {
            return '₹' + (value * exchangeRate).toFixed(2);
        }
    }
    
    async function toggleCurrency() {
        if (!exchangeRate) await fetchExchangeRate();
        const totalSalesElement = document.querySelector('#total-sales');
        const averageSalesElement = document.querySelector('#average-sales-value');
        const topProductsList = document.querySelectorAll('#top-products-list span[data-usd]');

        if (currency === 'USD') {
            totalSalesElement.innerHTML = '₹' + (parseFloat(totalSalesElement.getAttribute('data-usd')) * exchangeRate).toFixed(2);
            averageSalesElement.innerHTML = '₹' + (parseFloat(averageSalesElement.getAttribute('data-usd')) * exchangeRate).toFixed(2);
            topProductsList.forEach(product => {
                product.innerHTML = '₹' + (parseFloat(product.getAttribute('data-usd')) * exchangeRate).toFixed(2);
            });
            currency = 'INR';
        } else {
            totalSalesElement.innerHTML = '$' + parseFloat(totalSalesElement.getAttribute('data-usd')).toFixed(2);
            averageSalesElement.innerHTML = '$' + parseFloat(averageSalesElement.getAttribute('data-usd')).toFixed(2);
            topProductsList.forEach(product => {
                product.innerHTML = '$' + parseFloat(product.getAttribute('data-usd')).toFixed(2);
            });
            currency = 'USD';
        }
    }

    fetchExchangeRate();
    window.toggleCurrency = toggleCurrency; // Ensure the function is accessible globally
});
