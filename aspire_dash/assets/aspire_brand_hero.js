/* aspire_dash v0.102: make the brand_hero() video autoplay everywhere.
   React sets `muted` only as a DOM property, never the attribute, and Dash's html.Video has no playsInline:
   iOS Safari needs both ATTRIBUTES to autoplay inline. Dash renders pages late, so watch the DOM. */
(function () {
  // The opaque MP4 (Safari's path) is decoded through each browser's own colour pipeline, so its blue can land a
  // few levels off the CSS blue and show as a box. Sample the video's corner AS THIS BROWSER DECODES IT and paint
  // the hero that exact colour: seamless on any device/profile. The transparent WebM path needs none of this.
  // Only a sample near the expected blue (#002656 = 0,38,86) is trusted: some engines return black or nothing
  // for a video drawn to canvas, and painting the hero black would be far worse than a faint box.
  function plausible(d) {
    return d[3] > 200 && Math.abs(d[0] - 0) < 40 && Math.abs(d[1] - 38) < 40 && Math.abs(d[2] - 86) < 40;
  }
  function matchBackground(v, tries) {
    if (!/\.mp4(\?|$)/.test(v.currentSrc || "")) return;
    var d = null;
    try {
      var c = document.createElement("canvas");
      c.width = c.height = 1;
      var x = c.getContext("2d");
      x.drawImage(v, 2, 2, 6, 6, 0, 0, 1, 1);
      d = x.getImageData(0, 0, 1, 1).data;
    } catch (e) { d = null; /* tainted or not ready */ }
    if (!d || !plausible(d)) {
      if ((tries || 0) < 6) setTimeout(function () { matchBackground(v, (tries || 0) + 1); }, 250);
      return;                                    // never trusted: the CSS blue stays
    }
    var rgb = "rgb(" + d[0] + "," + d[1] + "," + d[2] + ")";
    var hero = v.closest(".aspire-brand-hero");
    var stage = v.closest(".aspire-brand-hero__stage");
    if (hero) hero.style.background = rgb;
    if (stage) stage.style.background = rgb;
  }
  function arm(v) {
    if (v.dataset.aspireArmed) return;
    v.dataset.aspireArmed = "1";
    v.addEventListener("loadeddata", function () { matchBackground(v); });
    v.addEventListener("playing", function () { matchBackground(v); }, { once: true });
    // Safari plays VP9 WebM but IGNORES its alpha (black box): give it the MP4 composited on the stage blue
    var ua = navigator.userAgent;
    var safari = /Safari/.test(ua) && !/Chrome|Chromium|CriOS|Edg|OPR|Firefox|FxiOS/.test(ua);
    if (safari) {
      v.querySelectorAll('source[type^="video/webm"]').forEach(function (s) { s.remove(); });
      v.load();
    }
    v.muted = true;
    v.setAttribute("muted", "");
    v.setAttribute("playsinline", "");
    v.setAttribute("webkit-playsinline", "");
    if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) { v.pause(); return; }
    var p = v.play();
    if (p && p.catch) p.catch(function () { /* autoplay refused: the poster stays visible */ });
  }
  function scan() {
    document.querySelectorAll("video.aspire-brand-hero__video").forEach(arm);
  }
  new MutationObserver(scan).observe(document.documentElement, { childList: true, subtree: true });
  document.addEventListener("DOMContentLoaded", scan);
})();
