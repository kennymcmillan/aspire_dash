/* Keep every rich hover card (aspire_dash.components.hovercard_graph) fully on
 * screen. Shipped into every app's assets/ by setup_app() (0.97.0); promoted from
 * the Development Testing Dashboard, where it was browser-verified at 1024/1366/1920.
 *
 * The direction flip in hovercard.py only guards the browser edge. The card was
 * still cut off at the LEFT (the fixed sidebar, and the page's scroll box edge)
 * and at the TOP (the sticky header, or a left/right card centred on a point near
 * the top of a chart). This watches for cards and, after dcc.Tooltip has placed
 * one, measures it against the real visible area and shifts it inside:
 *   visible area = viewport
 *                  minus the fixed .sidebar (left) and the .header (top)
 *                  intersected with every clipping (overflow != visible) ancestor.
 * The pointer arrow is hidden while a card is shifted, since it no longer lines
 * up with the point. Works on every page and inside the enlarge modal.
 */
(function () {
    var MARGIN = 8;

    function visibleArea(el) {
        var de = document.documentElement;
        var b = {left: 0, top: 0, right: de.clientWidth || window.innerWidth,
                 bottom: de.clientHeight || window.innerHeight};
        var inModal = !!(el.closest && el.closest('.modal'));
        if (!inModal) {
            var sb = document.querySelector('.sidebar');
            if (sb) {
                var sr = sb.getBoundingClientRect();
                if (sr.width > 0 && sr.right > b.left && sr.left <= 0) b.left = sr.right;
            }
            var hd = document.querySelector('.header');
            if (hd) {
                var pos = getComputedStyle(hd).position;
                var hr = hd.getBoundingClientRect();
                if ((pos === 'fixed' || pos === 'sticky') && hr.bottom > b.top) b.top = hr.bottom;
            }
        }
        for (var p = el.parentElement; p && p !== document.body; p = p.parentElement) {
            var cs = getComputedStyle(p);
            if (cs.overflowX !== 'visible' || cs.overflowY !== 'visible') {
                var r = p.getBoundingClientRect();
                b.left = Math.max(b.left, r.left);
                b.top = Math.max(b.top, r.top);
                b.right = Math.min(b.right, r.right);
                b.bottom = Math.min(b.bottom, r.bottom);
            }
        }
        return b;
    }

    function shift(box, r, M) {
        // how far to move [r.lo, r.hi] to sit inside [box.lo, box.hi]; low edge wins
        if (r.lo < box.lo + M) return box.lo + M - r.lo;
        if (r.hi > box.hi - M) return Math.max(box.hi - M - r.hi, box.lo + M - r.lo);
        return 0;
    }

    function clampOne(card) {
        var target = card.closest('.hover') || card.parentElement;
        if (!target) return;
        target.style.transform = '';
        target.classList.remove('hc-nudged');
        var r = card.getBoundingClientRect();
        if (!r.width || !r.height) return;
        var b = visibleArea(target);
        var dx = shift({lo: b.left, hi: b.right}, {lo: r.left, hi: r.right}, MARGIN);
        var dy = shift({lo: b.top, hi: b.bottom}, {lo: r.top, hi: r.bottom}, MARGIN);
        if (dx || dy) {
            target.style.transform = 'translate(' + Math.round(dx) + 'px,' + Math.round(dy) + 'px)';
            target.classList.add('hc-nudged');
        }
    }

    var busy = false, queued = false, observer = null;

    function clampAll() {
        queued = false;
        busy = true;
        observer.disconnect();
        try {
            document.querySelectorAll('.hovercard-tip .hover-card').forEach(clampOne);
        } finally {
            observe();
            busy = false;
        }
    }

    function schedule() {
        if (busy || queued) return;
        queued = true;
        requestAnimationFrame(function () { requestAnimationFrame(clampAll); });
    }

    function observe() {
        observer.observe(document.body, {childList: true, subtree: true,
                                         attributes: true, attributeFilter: ['style', 'class']});
    }

    function start() {
        observer = new MutationObserver(function (muts) {
            for (var i = 0; i < muts.length; i++) {
                var t = muts[i].target;
                if (t.closest && (t.closest('.dcc-tooltip-bounding-box') || t.closest('.hovercard-tip'))) {
                    schedule();
                    return;
                }
                if (muts[i].addedNodes && muts[i].addedNodes.length) {
                    for (var j = 0; j < muts[i].addedNodes.length; j++) {
                        var n = muts[i].addedNodes[j];
                        if (n.querySelector && (n.matches('.hover-card') || n.querySelector('.hover-card'))) {
                            schedule();
                            return;
                        }
                    }
                }
            }
        });
        observe();
        window.addEventListener('resize', schedule);
        window.addEventListener('scroll', schedule, true);
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
    else start();
})();
