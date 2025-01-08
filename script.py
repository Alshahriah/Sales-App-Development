                </script>
            </div>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.2/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    <script>
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
    </script>
</body>
</html>
