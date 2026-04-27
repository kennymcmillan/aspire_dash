/* Dark mode toggle — saves preference to localStorage */
document.addEventListener('DOMContentLoaded', function() {
    // Restore saved preference
    if (localStorage.getItem('aspire-dark-mode') === 'true') {
        document.documentElement.classList.add('dark');
    }

    // Toggle on button click
    document.addEventListener('click', function(e) {
        var btn = e.target.closest('#dark-mode-toggle');
        if (!btn) return;
        document.documentElement.classList.toggle('dark');
        var isDark = document.documentElement.classList.contains('dark');
        localStorage.setItem('aspire-dark-mode', isDark);
        // Update icon
        var icon = btn.querySelector('i');
        if (icon) {
            icon.className = isDark ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
        }
    });
});
