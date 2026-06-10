/* Lazy image loading for athlete photos (v0.50).
   Dash 4.1's html.Img rejects the native `loading` prop, so we lazy-load
   the classic way: render <img data-src="..."> via aspire_dash.lazy_img()
   and swap data-src -> src when the image nears the viewport.
   Inert unless img[data-src] elements exist on the page. */
document.addEventListener('DOMContentLoaded', function() {
    var io = new IntersectionObserver(function(entries) {
        entries.forEach(function(en) {
            if (!en.isIntersecting) return;
            var el = en.target;
            var src = el.getAttribute('data-src');
            if (src) {
                el.src = src;
                el.removeAttribute('data-src');
            }
            io.unobserve(el);
        });
    }, { rootMargin: '300px' });   // start fetching just before visible

    function observeAll(root) {
        if (!root.querySelectorAll) return;
        root.querySelectorAll('img[data-src]').forEach(function(img) {
            io.observe(img);
        });
    }

    // Dash re-renders pages client-side — watch for new nodes
    new MutationObserver(function(muts) {
        muts.forEach(function(m) {
            m.addedNodes.forEach(function(n) {
                if (n.nodeType !== 1) return;
                if (n.matches && n.matches('img[data-src]')) io.observe(n);
                observeAll(n);
            });
        });
    }).observe(document.body, { childList: true, subtree: true });

    observeAll(document);
});
