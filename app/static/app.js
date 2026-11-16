/**
 * CustomerHub Frontend Script
 * Provides progressive enhancements for notifications, search, and delete confirmations.
 */
document.addEventListener("DOMContentLoaded", function () {
    // Auto-dismiss alerts after 5 seconds if not error
    const alerts = document.querySelectorAll(".alert:not(.alert-danger)");
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = "opacity 0.4s ease, transform 0.4s ease";
            alert.style.opacity = "0";
            alert.style.transform = "translateY(-5px)";
            setTimeout(function () {
                alert.remove();
            }, 400);
        }, 5000);
    });

    // Handle delete confirmation dialogs if marked with data-confirm
    const confirmForms = document.querySelectorAll("form[data-confirm]");
    confirmForms.forEach(function (form) {
        form.addEventListener("submit", function (e) {
            const message = form.getAttribute("data-confirm") || "Are you sure you want to delete this customer? This action cannot be undone.";
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
});
