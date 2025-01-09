<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>
    <link rel="stylesheet" href="/static/admin.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        // Initialize variables using Jinja templating
        const totalBuyPrice = {{ total_buy_price }};
        const totalAmazonCommission = {{ total_amazon_commission }};
        const totalProfit = {{ total_profit }};
        
        const receivedOrders = {{ received_orders }};
        const returnedOrders = {{ returned_orders }};
        const pendingOrders = {{ pending_orders }};
        const shippedOrders = {{ shipped_orders }};
        const cancelledOrdersCount = {{ cancelled_orders_count }};
        
        const salesValueDates = [{% for date, value in sales_value %}'{{ date }}'{% if not loop.last %}, {% endif %}{% endfor %}];
        const salesValueValues = [{% for date, value in sales_value %}{{ value }}{% if not loop.last %}, {% endif %}{% endfor %}];
        
        const performanceDates = [{% for date, count in performance_orders %}'{{ date }}'{% if not loop.last %}, {% endif %}{% endfor %}];
        const performanceCounts = [{% for date, count in performance_orders %}{{ count }}{% if not loop.last %}, {% endif %}{% endfor %}];
        
        const salesByRegionLabels = [{% for region, value in sales_by_region %}'{{ region }}'{% if not loop.last %}, {% endif %}{% endfor %}];
        const salesByRegionValues = [{% for region, value in sales_by_region %}{{ value }}{% if not loop.last %}, {% endif %}{% endfor %}];
        
        const salesBySupplierLabels = [{% for supplier, count in sales_by_supplier %}'{{ supplier }}'{% if not loop.last %}, {% endif %}{% endfor %}];
        const salesBySupplierCounts = [{% for supplier, count in sales_by_supplier %}{{ count }}{% if not loop.last %}, {% endif %}{% endfor %}];
    </script>
</head>
<body>
    <div class="container">
        <h2>Dashboard</h2>
        <canvas id="profitMarginChart"></canvas>
        <canvas id="ordersSummaryChart"></canvas>
        <canvas id="salesValueChart"></canvas>
        <canvas id="performanceChart"></canvas>
        <canvas id="salesByRegionChart"></canvas>
        <canvas id="salesBySupplierChart"></canvas>
        <button class="toggle-btn" onclick="toggleCurrency()">Toggle Currency (USD/INR)</button>
    </div>
    <script src="/static/dashboard.js"></script> <!-- Include the new dashboard.js file -->
</body>
</html>
