/* aspire_dash section tabs (components.section_tabs, class .aspire-section-tabs). Shipped by setup_app().
   Only touches elements with that class, so it is inert in apps that do not use section_tabs.
   1. Keyboard: dbc 2.0 renders every tab link tabindex=-1 with one shared id. Roving tabindex: the active tab is
      in the Tab order, ArrowLeft/Right, Home, End move focus, Enter/Space open, aria-selected follows.
   2. Plotly charts drawn inside a hidden pane come out at the wrong width: fire `resize` after a switch.
   3. Sticky rows: --aspire-hdr = the sticky header's live height (rows stick at that top); a sub row stacks under
      its main row (--aspire-tabs-h on the sub row); a stuck row gets .aspire-section-tabs--stuck (soft shadow).
      Choosing a tab while stuck brings the top of its content back into view. */
(function () {
  "use strict";
  var SEL = ".aspire-section-tabs";

  function links(list) { return Array.prototype.slice.call(list.querySelectorAll(":scope > .nav-item > .nav-link")); }

  function roving(list) {
    var all = links(list);
    var anyActive = all.some(function (a) { return a.classList.contains("active"); });
    list.setAttribute("role", "tablist");
    all.forEach(function (a, i) {
      var on = a.classList.contains("active") || (!anyActive && i === 0);
      if (a.getAttribute("tabindex") !== (on ? "0" : "-1")) { a.setAttribute("tabindex", on ? "0" : "-1"); }
      if (a.getAttribute("aria-selected") !== String(on)) { a.setAttribute("aria-selected", String(on)); }
      if (a.getAttribute("role") !== "tab") { a.setAttribute("role", "tab"); }
      if (a.parentElement.getAttribute("role") !== "presentation") { a.parentElement.setAttribute("role", "presentation"); }
    });
  }

  function measure() {
    var h = document.querySelector(".header");
    var px = h ? Math.round(h.getBoundingClientRect().height) : 0;
    var root = document.documentElement;
    if (root.style.getPropertyValue("--aspire-hdr") !== px + "px") { root.style.setProperty("--aspire-hdr", px + "px"); }
  }

  function mainRowFor(sub) {
    var content = sub.parentElement && sub.parentElement.closest(".tab-content");
    var row = content && content.previousElementSibling;
    return row && row.matches && row.matches(SEL) ? row : null;
  }

  function stuck() {
    var root = document.documentElement;
    var top = parseFloat(getComputedStyle(root).getPropertyValue("--aspire-hdr")) || 0;
    document.querySelectorAll(SEL).forEach(function (t) {
      var want = top;
      if (t.classList.contains("aspire-section-tabs--sub")) {
        var main = mainRowFor(t);
        var mh = main ? Math.round(main.getBoundingClientRect().height) : 0;
        if (t.style.getPropertyValue("--aspire-tabs-h") !== mh + "px") { t.style.setProperty("--aspire-tabs-h", mh + "px"); }
        if (main) { main.classList.add("aspire-section-tabs--has-sub"); }
        want = top + mh;
      }
      var on = window.scrollY > 0 && Math.abs(t.getBoundingClientRect().top - want) < 2;
      if (t.classList.contains("aspire-section-tabs--stuck") !== on) { t.classList.toggle("aspire-section-tabs--stuck", on); }
    });
  }

  function all() { document.querySelectorAll(SEL).forEach(roving); measure(); stuck(); }

  document.addEventListener("click", function (e) {
    var link = e.target.closest && e.target.closest(SEL + " .nav-link");
    if (!link) { return; }
    var list = link.closest(SEL);
    var wasStuck = list.classList.contains("aspire-section-tabs--stuck");
    window.setTimeout(function () {
      all();
      window.dispatchEvent(new Event("resize"));
      if (wasStuck) {
        var content = list.nextElementSibling;
        if (content) { content.scrollIntoView({ block: "start" }); }
      }
    }, 60);
  });

  document.addEventListener("keydown", function (e) {
    var link = e.target.closest && e.target.closest(SEL + " .nav-link");
    if (!link) { return; }
    var list = link.closest(SEL);
    var items = links(list);
    var i = items.indexOf(link);
    var next = null;
    if (e.key === "ArrowRight") { next = items[(i + 1) % items.length]; }
    else if (e.key === "ArrowLeft") { next = items[(i - 1 + items.length) % items.length]; }
    else if (e.key === "Home") { next = items[0]; }
    else if (e.key === "End") { next = items[items.length - 1]; }
    else if (e.key === "Enter" || e.key === " ") { e.preventDefault(); link.click(); return; }
    if (next) {
      e.preventDefault();
      items.forEach(function (a) { a.setAttribute("tabindex", a === next ? "0" : "-1"); });
      next.focus();
      next.scrollIntoView({ block: "nearest", inline: "nearest" });
    }
  });

  /* Tabs arrive with page content (Dash renders on navigation): re-apply when the DOM changes, once per frame. */
  var queued = false;
  function schedule() {
    if (queued) { return; }
    queued = true;
    window.requestAnimationFrame(function () { queued = false; all(); });
  }
  new MutationObserver(schedule).observe(document.documentElement, { childList: true, subtree: true });
  window.addEventListener("resize", schedule);
  window.addEventListener("scroll", stuck, { passive: true });
  document.addEventListener("DOMContentLoaded", schedule);
  schedule();
})();
