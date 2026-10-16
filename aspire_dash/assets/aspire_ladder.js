/* aspire_dash 0.108 ladder motion (components/ladder.py, promoted from High Management Overview). Dash renders
   after load, so a MutationObserver finds each new .ad-lj-anim element and an IntersectionObserver adds .is-in when
   it comes into view (never a scroll listener). [data-replay] re-runs a card, [data-more] unfolds far rungs. */
(function () {
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); } });
  }, { threshold: 0.25 });
  function scan(root) {
    if (!root || !root.querySelectorAll) return;
    if (root.classList && root.classList.contains("ad-lj-anim") && !root.dataset.adLjSeen) { root.dataset.adLjSeen = "1"; io.observe(root); }
    root.querySelectorAll(".ad-lj-anim:not([data-ad-lj-seen])").forEach(function (el) { el.dataset.adLjSeen = "1"; io.observe(el); });
  }
  new MutationObserver(function (ms) { ms.forEach(function (m) { m.addedNodes.forEach(scan); }); })
    .observe(document.documentElement, { childList: true, subtree: true });
  document.addEventListener("DOMContentLoaded", function () { scan(document.body); });
  document.addEventListener("click", function (ev) {
    var m = ev.target.closest && ev.target.closest("[data-more]");      // the ladder's folded rungs (components/ladder.py)
    if (m) {
      var ld = m.closest(".ad-lj-ld");
      if (!ld) return;
      if (!m.dataset.label) m.dataset.label = m.textContent;
      var open = ld.classList.toggle("is-open");
      m.textContent = open ? "Show fewer rungs" : m.dataset.label;
      m.setAttribute("aria-expanded", open ? "true" : "false");
      return;
    }
    var b = ev.target.closest && ev.target.closest("[data-replay]");
    if (!b) return;
    var card = b.closest(".ad-lj-card");
    if (!card) return;
    var els = card.querySelectorAll(".ad-lj-anim");
    card.classList.add("ad-lj-reset");                    // jump back to the start without animating backwards
    els.forEach(function (el) { el.classList.remove("is-in"); });
    void card.offsetWidth;
    card.classList.remove("ad-lj-reset");
    requestAnimationFrame(function () { els.forEach(function (el) { el.classList.add("is-in"); }); });
  });
})();
