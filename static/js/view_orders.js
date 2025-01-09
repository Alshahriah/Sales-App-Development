document.getElementById('searchBar').addEventListener('input', function() {
    var searchTerm = this.value.toLowerCase();
    var orderRows = document.querySelectorAll('#orderTable tr');

    orderRows.forEach(function(row) {
        var productName = row.cells[0].textContent.toLowerCase();
        var supplierName = row.cells[1].textContent.toLowerCase();
        var buyerName = row.cells[9].textContent.toLowerCase();

        if (productName.includes(searchTerm) || supplierName.includes(searchTerm) || buyerName.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
});
