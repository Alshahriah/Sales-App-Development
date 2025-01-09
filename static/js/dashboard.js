// const totalBuyPrice = {{ total_buy_price }};
// const totalAmazonCommission = {{ total_amazon_commission }};
// const totalProfit = {{ total_profit }};

// const receivedOrders = {{ received_orders }};
// const returnedOrders = {{ returned_orders }};
// const pendingOrders = {{ pending_orders }};
// const shippedOrders = {{ shipped_orders }};
// const cancelledOrdersCount = {{ cancelled_orders_count }};

// const salesValueDates = [{% for date, value in sales_value %}'{{ date }}'{% if not loop.last %}, {% endif %}{% endfor %}];
// const salesValueValues = [{% for date, value in sales_value %}{{ value }}{% if not loop.last %}, {% endif %}{% endfor %}];

// const performanceDates = [{% for date, count in performance_orders %}'{{ date }}'{% if not loop.last %}, {% endif %}{% endfor %}];
// const performanceCounts = [{% for date, count in performance_orders %}{{ count }}{% if not loop.last %}, {% endif %}{% endfor %}];

// const salesByRegionLabels = [{% for region, value in sales_by_region %}'{{ region }}'{% if not loop.last %}, {% endif %}{% endfor %}];
// const salesByRegionValues = [{% for region, value in sales_by_region %}{{ value }}{% if not loop.last %}, {% endif %}{% endfor %}];

// const salesBySupplierLabels = [{% for supplier, count in sales_by_supplier %}'{{ supplier }}'{% if not loop.last %}, {% endif %}{% endfor %}];
// const salesBySupplierCounts = [{% for supplier, count in sales_by_supplier %}{{ count }}{% if not loop.last %}, {% endif %}{% endfor %}];

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
        const salePrices = document.querySelectorAll('.sale-price');
        const buyPrices = document.querySelectorAll('.buy-price a');
        const commissionValues = document.querySelectorAll('.commission-value');
        
        if (currency === 'USD') {
            salePrices.forEach(price => price.innerHTML = formatCurrency(price.getAttribute('data-usd'), 'INR'));
            buyPrices.forEach(price => price.innerHTML = formatCurrency(price.parentElement.getAttribute('data-usd'), 'INR'));
            commissionValues.forEach(value => value.innerHTML = formatCurrency(value.getAttribute('data-usd'), 'INR'));
            currency = 'INR';
        } else {
            salePrices.forEach(price => price.innerHTML = formatCurrency(price.getAttribute('data-usd'), 'USD'));
            buyPrices.forEach(price => price.innerHTML = formatCurrency(price.parentElement.getAttribute('data-usd'), 'USD'));
            commissionValues.forEach(value => value.innerHTML = formatCurrency(value.getAttribute('data-usd'), 'USD'));
            currency = 'USD';
        }
    }
    fetchExchangeRate();
});
