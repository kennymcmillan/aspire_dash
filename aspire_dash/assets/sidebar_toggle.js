/* Sidebar toggle — pure JS, no Dash callback needed.
   Desktop / iPad landscape (>=1024px): collapse/expand pushes the layout.
   Phones / iPad portrait (<1024px): off-canvas drawer + backdrop overlay. */
document.addEventListener('DOMContentLoaded', function() {
    var MOBILE = window.matchMedia('(max-width: 1023px)');

    function getBackdrop() {
        var el = document.getElementById('sidebar-backdrop');
        if (!el) {
            el = document.createElement('div');
            el.id = 'sidebar-backdrop';
            el.className = 'sidebar-backdrop';
            document.body.appendChild(el);
            el.addEventListener('click', closeMobileDrawer);
        }
        return el;
    }

    function closeMobileDrawer() {
        var sidebar = document.getElementById('sidebar');
        if (sidebar) sidebar.classList.remove('sidebar-mobile-open');
        var el = document.getElementById('sidebar-backdrop');
        if (el) el.classList.remove('is-visible');
    }

    // Event delegation — the button may render after this script runs
    document.addEventListener('click', function(e) {
        var btn = e.target.closest('#sidebar-toggle');
        if (btn) {
            var sidebar = document.getElementById('sidebar');
            var main = document.getElementById('main-area');
            if (MOBILE.matches) {
                if (!sidebar) return;
                var open = sidebar.classList.toggle('sidebar-mobile-open');
                getBackdrop().classList.toggle('is-visible', open);
            } else {
                if (sidebar) sidebar.classList.toggle('sidebar-collapsed');
                if (main) main.classList.toggle('main-area-expanded');
            }
            return;
        }
        // Tapping a nav link inside the open drawer closes it
        if (MOBILE.matches && e.target.closest('.sidebar a')) {
            closeMobileDrawer();
        }
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeMobileDrawer();
    });

    // Rotating an iPad / resizing past the breakpoint: clear drawer state
    var onChange = function(m) { if (!m.matches) closeMobileDrawer(); };
    if (MOBILE.addEventListener) MOBILE.addEventListener('change', onChange);
    else if (MOBILE.addListener) MOBILE.addListener(onChange); // older Safari
});
