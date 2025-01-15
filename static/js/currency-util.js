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
    const totalSales = document.querySelector('#total-sales');
    const averageSales = document.querySelector('#average-sales-value');
    const topProductsList = document.querySelectorAll('#top-products-list span[data-usd]');
    
    if (currency === 'USD') {
        salePrices?.forEach(price => price.innerHTML = formatCurrency(price.getAttribute('data-usd'), 'INR'));
        buyPrices?.forEach(price => price.innerHTML = formatCurrency(price.parentElement.getAttribute('data-usd'), 'INR'));
        commissionValues?.forEach(value => value.innerHTML = formatCurrency(value.getAttribute('data-usd'), 'INR'));
        
        // Dashboard specific elements
        if (totalSales) totalSales.innerHTML = '₹' + (parseFloat(totalSales.getAttribute('data-usd')) * exchangeRate).toFixed(2);
        if (averageSales) averageSales.innerHTML = '₹' + (parseFloat(averageSales.getAttribute('data-usd')) * exchangeRate).toFixed(2);
        topProductsList?.forEach(product => {
            product.innerHTML = '₹' + (parseFloat(product.getAttribute('data-usd')) * exchangeRate).toFixed(2);
        });
        
        currency = 'INR';
    } else {
        salePrices?.forEach(price => price.innerHTML = formatCurrency(price.getAttribute('data-usd'), 'USD'));
        buyPrices?.forEach(price => price.innerHTML = formatCurrency(price.parentElement.getAttribute('data-usd'), 'USD'));
        commissionValues?.forEach(value => value.innerHTML = formatCurrency(value.getAttribute('data-usd'), 'USD'));
        
        // Dashboard specific elements
        if (totalSales) totalSales.innerHTML = '$' + parseFloat(totalSales.getAttribute('data-usd')).toFixed(2);
        if (averageSales) averageSales.innerHTML = '$' + parseFloat(averageSales.getAttribute('data-usd')).toFixed(2);
        topProductsList?.forEach(product => {
            product.innerHTML = '$' + parseFloat(product.getAttribute('data-usd')).toFixed(2);
        });
        
        currency = 'USD';
    }
}

document.addEventListener('DOMContentLoaded', fetchExchangeRate);
window.toggleCurrency = toggleCurrency;
