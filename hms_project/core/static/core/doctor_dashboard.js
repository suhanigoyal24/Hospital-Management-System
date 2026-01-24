// core/static/core/doctor_dashboard.js

document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-btn');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            const confirmed = confirm("Are you sure you want to delete this slot?");
            if (!confirmed) {
                event.preventDefault(); // stop link/button if cancelled
            }
        });
    });
});
