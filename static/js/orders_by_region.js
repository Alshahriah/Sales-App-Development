document.addEventListener('DOMContentLoaded', function() {
    const deleteForms = document.querySelectorAll('form[action^="/delete/"]');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent the form from submitting immediately
            const confirmation = confirm('Are you sure you want to delete this order?');
            if (confirmation) {
                form.submit(); // Submit the form if the user confirms
            }
        });
    });
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
        commissionValues.forEach value => value.innerHTML = formatCurrency(value.getAttribute('data-usd'), 'USD'));
        currency = 'USD';
    }
}

document.addEventListener('DOMContentLoaded', fetchExchangeRate);
