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