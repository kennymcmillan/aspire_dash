/* Sidebar toggle — pure JS, no Dash callback needed */
document.addEventListener('DOMContentLoaded', function() {
    // Use event delegation since the button may not exist yet
    document.addEventListener('click', function(e) {
        var btn = e.target.closest('#sidebar-toggle');
        if (!btn) return;
        var sidebar = document.getElementById('sidebar');
        var main = document.getElementById('main-area');
        if (sidebar) sidebar.classList.toggle('sidebar-collapsed');
        if (main) main.classList.toggle('main-area-expanded');
    });
});
