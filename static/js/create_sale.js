// Function to set the sale_date to today's date in India
function setSaleDateToToday() {
    const saleDateInput = document.getElementById('sale_date');
    const today = new Date().toLocaleString('en-US', { timeZone: 'Asia/Kolkata' });
    const localDate = new Date(today);
    const formattedDate = localDate.toISOString().split('T')[0];
    saleDateInput.value = formattedDate;
}

// Set the sale_date when the page loads
window.onload = setSaleDateToToday;
