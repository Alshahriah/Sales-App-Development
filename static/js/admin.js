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

    const rows = document.querySelectorAll('tbody tr');
    rows.forEach(row => {
        const statusSelect = row.querySelector('select.status-dropdown');
        const status = statusSelect.value;
        const parentCell = statusSelect.parentElement;
        const indicator = parentCell.querySelector('.delivery-indicator');
        indicator.classList.add(status.toLowerCase());

        // Add event listener for change
        statusSelect.addEventListener('change', async function() {
            const newStatus = this.value;
            const saleId = statusSelect.getAttribute('data-sale-id');
            indicator.className = `delivery-indicator ${newStatus.toLowerCase()}`;
            const statusText = parentCell.querySelector('.delivery-status-text');
            statusText.textContent = newStatus;

            const response = await fetch(`/update_status/${saleId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ delivery_status: newStatus })
            });

            if (response.ok) {
                alert('Status updated successfully'); // Single alert for success
            } else {
                const errorData = await response.json();
                console.error('Error updating status:', errorData);
                alert('Failed to update status');
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
        commissionValues.forEach(value => value.innerHTML = formatCurrency(value.getAttribute('data-usd'), 'USD'));
        currency = 'USD';
    }
}

document.addEventListener('DOMContentLoaded', fetchExchangeRate);
