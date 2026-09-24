/* aspire_dash.asian_games: small DOM behaviours that need no callback.
 *  - filter the Disciplines mega-menu as you type
 *  - burger button opens and closes the mobile nav
 *  - picking a mega-menu tile closes the menu
 * Event delegation on document, so it works for pages rendered later by Dash. */
(function () {
    document.addEventListener('input', function (e) {
        var box = e.target.closest && e.target.closest('.ag-mega__search');
        if (!box) return;
        var q = (e.target.value || '').trim().toLowerCase();
        var grid = box.closest('.ag-mega__panel').querySelector('.ag-mega__grid');
        if (!grid) return;
        var shown = 0;
        grid.querySelectorAll('.ag-mega__tile').forEach(function (t) {
            var hit = !q || (t.getAttribute('data-label') || t.textContent).toLowerCase().indexOf(q) !== -1;
            t.hidden = !hit;
            if (hit) shown++;
        });
        grid.classList.toggle('is-empty', shown === 0);
    });

    document.addEventListener('click', function (e) {
        var burger = e.target.closest && e.target.closest('.ag-burger');
        if (burger) {
            var nav = burger.closest('.ag-topnav');
            if (nav) {
                var open = nav.classList.toggle('is-open');
                burger.setAttribute('aria-expanded', open ? 'true' : 'false');
                var icon = burger.querySelector('i');
                if (icon) icon.className = open ? 'fa-solid fa-xmark' : 'fa-solid fa-bars';
            }
            return;
        }
        var tile = e.target.closest && e.target.closest('.ag-mega__tile, .ag-nav__link');
        if (tile) {
            if (document.activeElement && document.activeElement.blur) document.activeElement.blur();
            var topnav = tile.closest('.ag-topnav');
            if (topnav && topnav.classList.contains('is-open')) {
                topnav.classList.remove('is-open');
                var b = topnav.querySelector('.ag-burger i');
                if (b) b.className = 'fa-solid fa-bars';
            }
        }
    });
})();
