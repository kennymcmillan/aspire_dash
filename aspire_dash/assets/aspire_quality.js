/* aspire_dash app-quality kit (opt-in). Shipped by setup_app() to every app, but does NOTHING unless the page
   carries the class "aspire-quality" (setup_app(app, quality=True) puts it on <html>; or add it to any wrapper).
   Applied to the rendered DOM and re-applied whenever Dash re-renders:
   1. Page title in the top bar: the page's page_head() (h1 + lead in .aspire-page-head) is copied into the
      header (#aspire-page-title / #aspire-page-subtitle); CSS hides the in-page copy visually. Pages without a
      page_head get the header's original title back.
   2. Sidebar "you are here": .sidebar-link.active + aria-current on the link for the current path.
   3. Accessibility floor: lang="en"; landmarks (nav / main / banner) and a "Skip to content" link; the menu
      button gets a name + aria-expanded; the closed phone drawer is inert; wide table scrollers become
      focusable labelled regions; unlabelled search/chat inputs get an aria-label; flags and the logo get alt. */
(function () {
  "use strict";
  var MOBILE = window.matchMedia("(max-width: 1023px)");

  function on() {
    return document.documentElement.classList.contains("aspire-quality") || !!document.querySelector(".aspire-quality");
  }

  function setText(el, text) { if (el && el.textContent !== text) { el.textContent = text; } }

  function syncTitle() {
    var t = document.getElementById("aspire-page-title");
    if (!t) { return; }
    var sub = document.getElementById("aspire-page-subtitle");
    if (t.dataset.aspireDefault === undefined) {
      t.dataset.aspireDefault = t.textContent;
      if (sub) { sub.dataset.aspireDefault = sub.textContent; sub.dataset.aspireDisplay = sub.style.display || ""; }
    }
    var head = document.querySelector(".page-content .aspire-page-head");
    var h1 = head && head.querySelector(".aspire-page-head__title");
    var lead = head && head.querySelector(".aspire-page-head__lead");
    setText(t, h1 ? h1.textContent.trim() : t.dataset.aspireDefault);
    if (!sub) { return; }
    var s = h1 ? (lead ? lead.textContent.trim() : "") : sub.dataset.aspireDefault;
    setText(sub, s);
    sub.title = s;
    var display = s ? "" : "none";
    if (sub.style.display !== display) { sub.style.display = display; }
  }

  function markSidebar() {
    var path = window.location.pathname.replace(/\/+$/, "") || "/";
    var links = Array.prototype.slice.call(document.querySelectorAll("#sidebar a.sidebar-link"));
    var best = null, bestLen = -1;
    links.forEach(function (a) {
      var href = (a.getAttribute("href") || "").split("?")[0].split("#")[0].replace(/\/+$/, "") || "/";
      var hit = href === path || (href !== "/" && path.indexOf(href + "/") === 0);
      if (hit && href.length > bestLen) { best = a; bestLen = href.length; }
    });
    links.forEach(function (a) {
      var isOn = a === best;
      if (a.classList.contains("active") !== isOn) { a.classList.toggle("active", isOn); }
      if (isOn) { if (a.getAttribute("aria-current") !== "page") { a.setAttribute("aria-current", "page"); } }
      else if (a.hasAttribute("aria-current")) { a.removeAttribute("aria-current"); }
    });
  }

  function attr(el, name, value) { if (el && el.getAttribute(name) !== value) { el.setAttribute(name, value); } }

  function a11y() {
    attr(document.documentElement, "lang", document.documentElement.getAttribute("lang") || "en");
    var main = document.querySelector(".page-content");
    if (main) {
      if (!main.id) { main.id = "aspire-main"; }
      attr(main, "role", "main");
      attr(main, "tabindex", "-1");
    }
    var skip = document.getElementById("aspire-skip");
    if (!skip && main && document.body) {
      skip = document.createElement("a");
      skip.id = "aspire-skip"; skip.className = "aspire-skip"; skip.textContent = "Skip to content";
      document.body.insertBefore(skip, document.body.firstChild);
    }
    if (skip && main) { attr(skip, "href", "#" + main.id); }

    var side = document.getElementById("sidebar");
    if (side) {
      attr(side, "role", "navigation");
      attr(side, "aria-label", side.getAttribute("aria-label") || "Main menu");
      var open = MOBILE.matches ? side.classList.contains("sidebar-mobile-open") : !side.classList.contains("sidebar-collapsed");
      if (MOBILE.matches && !open) { attr(side, "inert", ""); attr(side, "aria-hidden", "true"); }
      else {
        if (side.hasAttribute("inert")) { side.removeAttribute("inert"); }
        if (side.hasAttribute("aria-hidden")) { side.removeAttribute("aria-hidden"); }
      }
      var btn = document.getElementById("sidebar-toggle");
      if (btn) {
        attr(btn, "aria-label", btn.getAttribute("aria-label") || "Menu");
        attr(btn, "aria-controls", "sidebar");
        attr(btn, "aria-expanded", String(open));
      }
    }
    attr(document.querySelector(".header"), "role", "banner");
    document.querySelectorAll(".aspire-data-table-scroll").forEach(function (s) {
      if (s.scrollWidth > s.clientWidth + 2) {
        attr(s, "tabindex", "0"); attr(s, "role", "region");
        if (!s.getAttribute("aria-label")) { s.setAttribute("aria-label", "Table, scrolls sideways"); }
      }
    });
    var chat = document.getElementById("aspire-chat-input");
    if (chat && !chat.getAttribute("aria-label")) { chat.setAttribute("aria-label", "Your question for the assistant"); }
    document.querySelectorAll("input[type=search], input[type=text][placeholder]").forEach(function (i) {
      if (!i.getAttribute("aria-label") && !i.getAttribute("aria-labelledby") && !(i.id && document.querySelector("label[for='" + i.id + "']"))) {
        i.setAttribute("aria-label", i.getAttribute("placeholder") || "Search");
      }
    });
    document.querySelectorAll("img.flag-chip__img:not([alt])").forEach(function (i) { i.setAttribute("alt", i.getAttribute("title") || ""); });
    document.querySelectorAll("img[src*='aspire-logo']:not([alt])").forEach(function (i) { i.setAttribute("alt", "Aspire Academy"); });
  }

  function apply() {
    if (!on()) { return; }
    syncTitle();
    markSidebar();
    a11y();
  }

  var pending = false;
  function schedule() {
    if (pending) { return; }
    pending = true;
    window.requestAnimationFrame(function () { pending = false; apply(); });
  }
  new MutationObserver(schedule).observe(document.documentElement,
    { childList: true, subtree: true, attributes: true, attributeFilter: ["class"] });
  if (MOBILE.addEventListener) { MOBILE.addEventListener("change", schedule); } else if (MOBILE.addListener) { MOBILE.addListener(schedule); }
  window.addEventListener("popstate", schedule);
  document.addEventListener("DOMContentLoaded", schedule);
  schedule();
})();
