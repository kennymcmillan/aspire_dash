/* aspire-chat.js (M7 2026-08-30, hardened v0.100.0, relay v0.101.0 2026-10-01): the Aspire sports chatbot client.
   Plain JS, no build step. Two uses:
     1. window.AspireChat.stream(engineUrl, {question, sport, thread_id, user_id}, handlers, {signal})
        for React/Next/vanilla pages (POST {engineUrl}/api/agent/ask/stream, Server-Sent Events).
        handlers: onThread, onStatus, onToken, onDone, onError, onAbort.
     2. window.dash_clientside.aspire_chat.* : the Dash glue used by aspire_dash.components.chat_panel.
   SSE lines are `data: <json>` with type in thread | status | token | done | error.

   Panel behaviour (per id prefix, so two panels can share a page):
   - one stream at a time: send() refuses while a stream is in flight; input read-only + Send disabled
     until done / error / abort.
   - Stop button or Esc aborts (AbortController); Retry on an error re-sends the last question; Copy on
     every finished answer (navigator.clipboard, execCommand fallback).
   - chips, starters, Stop, Retry, Copy are all handled by ONE delegated click listener
     (event.target.closest), never document.activeElement (Safari does not focus buttons on click).
   - the transcript is mirrored to sessionStorage under aspire-chat:<prefix>:<thread_id> and re-rendered
     on load; "New chat" clears both.
   - md() escapes HTML FIRST, then adds markup, so engine text can never inject tags.
   - v0.101.0 backends: config.backend "relay" (default) | "local" POST to THIS app's server at
     <requests_pathname_prefix>api/agent/ask/stream (prefix read from Dash's #_dash-config, so it works under
     Connect's /content/<guid>/); only "engine" POSTs to config.engine_url. A non-200 reply's SSE error
     event text (empty / too long / rate limit) is shown in the error bubble. */
(function () {
  "use strict";

  var VERSION = "0.101.0";

  async function stream(engineUrl, body, handlers, opts) {
    handlers = handlers || {};
    opts = opts || {};
    var signal = opts.signal;
    function aborted() { return !!(signal && signal.aborted); }
    var res;
    try {
      res = await fetch(engineUrl.replace(/\/$/, "") + "/api/agent/ask/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
        body: JSON.stringify(body),
        signal: signal,
      });
    } catch (e) {
      if (aborted()) { if (handlers.onAbort) handlers.onAbort(); }
      else if (handlers.onError) handlers.onError("network: " + e);
      return null;
    }
    if (!res.ok || !res.body) {
      var msg = "HTTP " + res.status;
      try {
        var txt = await res.text(), m = /data:\s*(\{.*\})/.exec(txt || "");
        if (m) { var ev0 = JSON.parse(m[1]); if (ev0 && ev0.error) msg = ev0.error; }
      } catch (e) {}
      if (handlers.onError) handlers.onError(msg);
      return null;
    }
    var reader = res.body.getReader();
    var dec = new TextDecoder();
    var buf = "";
    var done = null, errored = false;
    try {
      while (true) {
        var chunk = await reader.read();
        if (chunk.done) break;
        buf += dec.decode(chunk.value, { stream: true });
        var parts = buf.split("\n\n");
        buf = parts.pop();
        for (var i = 0; i < parts.length; i++) {
          var line = parts[i].trim();
          if (line.indexOf("data:") !== 0) continue;
          var ev;
          try { ev = JSON.parse(line.slice(5).trim()); } catch (e) { continue; }
          if (ev.type === "thread" && handlers.onThread) handlers.onThread(ev.thread_id);
          else if (ev.type === "token" && handlers.onToken) handlers.onToken(ev.text || "", ev.node);
          else if (ev.type === "status" && handlers.onStatus) handlers.onStatus(ev.text || ev.node || "");
          else if (ev.type === "done") { done = ev; if (handlers.onDone) handlers.onDone(ev); }
          else if (ev.type === "error") { errored = true; if (handlers.onError) handlers.onError(ev.error || "engine error"); }
        }
      }
    } catch (e) {
      if (aborted()) { if (handlers.onAbort) handlers.onAbort(); }
      else if (handlers.onError) handlers.onError("stream: " + e);
      return null;
    }
    if (!done && !errored && handlers.onError) handlers.onError("the stream ended without an answer");
    return done;
  }

  /* ---------------------------------------------------------------- markdown */
  function esc(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  /* inline markup on ALREADY-ESCAPED text. Code spans and links are swapped out for placeholders first so
     bold/italic rules never reach inside a URL or a code span. Only http(s) links become anchors. */
  function inline(s) {
    var slots = [];
    function hold(h) { slots.push(h); return "\u0000" + (slots.length - 1) + "\u0000"; }
    s = s.replace(/`([^`]+)`/g, function (_, c) { return hold("<code>" + c + "</code>"); });
    s = s.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)"]+)\)/g, function (_, t, u) {
      return hold('<a href="' + u + '" target="_blank" rel="noopener noreferrer">' + t + "</a>");
    });
    s = s.replace(/\*\*([^*]+?)\*\*/g, "<strong>$1</strong>").replace(/__([^_]+?)__/g, "<strong>$1</strong>");
    s = s.replace(/(^|[^*\w])\*([^*\s][^*]*?)\*(?!\*)/g, "$1<em>$2</em>");
    s = s.replace(/(^|[^_\w])_([^_\s][^_]*?)_(?![_\w])/g, "$1<em>$2</em>");
    return s.replace(/\u0000(\d+)\u0000/g, function (_, i) { return slots[+i]; });
  }

  function md(text) {
    var lines = esc(text || "").replace(/\r\n?/g, "\n").split("\n");
    var out = [], list = null, table = null, code = null;
    function closeList() { if (list) { out.push("</" + list + ">"); list = null; } }
    function closeTable() {
      if (!table) return;
      var h = '<div class="aspire-chat-table-wrap"><table class="table table-sm aspire-chat-table">';
      h += "<thead><tr>" + table.head.map(function (c) { return "<th>" + inline(c) + "</th>"; }).join("") + "</tr></thead><tbody>";
      h += table.rows.map(function (r) { return "<tr>" + r.map(function (c) { return "<td>" + inline(c) + "</td>"; }).join("") + "</tr>"; }).join("");
      out.push(h + "</tbody></table></div>");
      table = null;
    }
    for (var i = 0; i < lines.length; i++) {
      var l = lines[i];
      if (code !== null) {                                   // inside a fenced block: verbatim (already escaped)
        if (/^\s*```/.test(l)) { out.push('<pre class="aspire-chat-code"><code>' + code.join("\n") + "</code></pre>"); code = null; }
        else code.push(l);
        continue;
      }
      if (/^\s*```/.test(l)) { closeList(); closeTable(); code = []; continue; }
      if (/^\s*\|.*\|\s*$/.test(l)) {
        closeList();
        if (/^\s*\|[\s\-:|]+\|\s*$/.test(l)) continue;      // the |---|---| separator row
        var cells = l.trim().replace(/^\||\|$/g, "").split("|").map(function (c) { return c.trim(); });
        if (!table) table = { head: cells, rows: [] }; else table.rows.push(cells);
        continue;
      }
      closeTable();
      var m;
      if ((m = /^\s*[-*+]\s+(.*)$/.exec(l))) {
        if (list !== "ul") { closeList(); out.push("<ul>"); list = "ul"; }
        out.push("<li>" + inline(m[1]) + "</li>");
        continue;
      }
      if ((m = /^\s*(\d+)[.)]\s+(.*)$/.exec(l))) {
        if (list !== "ol") { closeList(); out.push(m[1] === "1" ? "<ol>" : '<ol start="' + (+m[1]) + '">'); list = "ol"; }
        out.push("<li>" + inline(m[2]) + "</li>");
        continue;
      }
      closeList();
      if ((m = /^(#{1,6})\s+(.*)$/.exec(l))) {
        var lvl = Math.min(6, m[1].length + 3);               // # -> h4 ... keeps headings modest in a bubble
        out.push("<h" + lvl + ">" + inline(m[2]) + "</h" + lvl + ">");
      } else if (l.trim() === "") out.push('<div class="aspire-chat-gap"></div>');
      else out.push("<p>" + inline(l) + "</p>");
    }
    if (code !== null) out.push('<pre class="aspire-chat-code"><code>' + code.join("\n") + "</code></pre>");  // unclosed while streaming
    closeList(); closeTable();
    return out.join("");
  }

  /* ---------------------------------------------------------------- panel state */
  var panels = {};   // prefix -> {config, busy, controller, thread, msgs, lastQ, raf}
  function panel(p) {
    if (!panels[p]) panels[p] = { gen: 0, config: null, busy: false, controller: null, thread: null, msgs: [], lastQ: null, raf: 0 };
    return panels[p];
  }
  function el(p, k) { return document.getElementById(p + "-" + k); }
  function nu() { return window.dash_clientside ? window.dash_clientside.no_update : undefined; }

  function storeKey(p, thread) { return "aspire-chat:" + p + ":" + thread; }
  function ss() { try { return window.sessionStorage; } catch (e) { return null; } }
  function persist(p) {
    var st = panel(p), s = ss();
    if (!s || !st.thread) return;
    try { s.setItem(storeKey(p, st.thread), JSON.stringify(st.msgs.slice(-200))); } catch (e) {}
  }
  function loadTranscript(p, thread) {
    var s = ss();
    if (!s || !thread) return [];
    try { var v = JSON.parse(s.getItem(storeKey(p, thread)) || "[]"); return Array.isArray(v) ? v : []; } catch (e) { return []; }
  }
  function dropTranscript(p, thread) { var s = ss(); if (s && thread) try { s.removeItem(storeKey(p, thread)); } catch (e) {} }

  function setStore(id, data) {
    /* write a dcc.Store from JS via dash_clientside.set_props (Dash >= 2.16) */
    if (window.dash_clientside && window.dash_clientside.set_props) window.dash_clientside.set_props(id, { data: data });
  }

  /* M4: a stable anonymous user id per browser (localStorage) so the engine can remember this coach's athletes
     across threads and sessions; apps with a login can set window.AspireChat.userId instead. */
  /* Where the browser sends questions: this app's own server (relay/local) or the engine (engine mode). */
  function dashPrefix() {
    try {
      var c = document.getElementById("_dash-config");
      var pre = c ? JSON.parse(c.textContent).requests_pathname_prefix : null;
      return (pre || "/").replace(/\/$/, "");
    } catch (e) { return ""; }
  }
  function apiBase(cfg) {
    if (cfg && cfg.backend === "engine") return (cfg.engine_url || "").replace(/\/$/, "");
    return dashPrefix();
  }

  function userId() {
    if (window.AspireChat && window.AspireChat.userId) return window.AspireChat.userId;
    try {
      var k = "aspire-chat-user", v = localStorage.getItem(k);
      if (!v) { v = "anon-" + Math.random().toString(36).slice(2, 10) + Date.now().toString(36); localStorage.setItem(k, v); }
      return v;
    } catch (e) { return null; }
  }

  /* ---------------------------------------------------------------- rendering */
  function bubble(role, html) {
    var d = document.createElement("div");
    d.className = "aspire-chat-bubble aspire-chat-" + role;
    var b = document.createElement("div");
    b.className = "aspire-chat-body";
    b.innerHTML = html;
    d.appendChild(b);
    return d;
  }
  function addActions(bot, raw) {
    bot._raw = raw;
    var a = document.createElement("div");
    a.className = "aspire-chat-actions";
    a.innerHTML = '<button type="button" class="aspire-chat-action" data-action="copy" title="Copy this answer">Copy</button>';
    bot.appendChild(a);
  }
  function errorBubble(msg) {
    var d = bubble("error",
      '<div class="aspire-chat-error-title">Sorry, that did not work.</div>' +
      '<div class="aspire-chat-error-detail">' + esc(msg) + "</div>");
    var a = document.createElement("div");
    a.className = "aspire-chat-actions";
    a.innerHTML = '<button type="button" class="aspire-chat-action" data-action="retry">Retry</button>';
    d.appendChild(a);
    return d;
  }
  function renderMsg(m) {
    if (m.role === "user") return bubble("user", esc(m.text));
    if (m.role === "error") return errorBubble(m.text);
    var b = bubble("assistant", md(m.text) + (m.stopped ? '<div class="aspire-chat-note">Stopped.</div>' : ""));
    addActions(b, m.text);
    return b;
  }
  function welcome(p) {
    var st = panel(p), msgs = el(p, "messages");
    if (!msgs || !st.config || !st.config.welcome) return;
    var w = document.createElement("div");
    w.className = "aspire-chat-welcome";
    w.textContent = st.config.welcome;
    msgs.appendChild(w);
  }
  function clearWelcome(msgs) { var w = msgs && msgs.querySelector(".aspire-chat-welcome"); if (w) w.remove(); }
  function scroll(msgs) { if (msgs) msgs.scrollTop = msgs.scrollHeight; }

  function lock(p, on) {
    var st = panel(p), input = el(p, "input"), send = el(p, "send"), stop = el(p, "stop"), root = el(p, "messages");
    st.busy = on;
    if (input) { input.readOnly = on; input.setAttribute("aria-busy", on ? "true" : "false"); }
    if (send) send.disabled = on;
    if (stop) stop.hidden = !on;
    if (root) root.setAttribute("aria-busy", on ? "true" : "false");
    if (!on) { setStore(p + "-stream-state", "idle"); if (input) try { input.focus({ preventScroll: true }); } catch (e) {} }
  }

  /* THE send path (button, Enter, chip, starter, Retry all land here). Returns false when refused. */
  function startSend(p, q, sport) {
    var st = panel(p), cfg = st.config, msgs = el(p, "messages"), status = el(p, "status");
    q = (q || "").trim();
    if (!q || !cfg || !msgs) return false;
    if (st.busy) return false;                               // one stream at a time: Enter double-fire, chip mid-stream
    lock(p, true);
    st.lastQ = q;
    clearWelcome(msgs);
    msgs.appendChild(bubble("user", esc(q)));
    st.msgs.push({ role: "user", text: q });
    persist(p);
    var bot = bubble("assistant", '<span class="aspire-chat-thinking">thinking...</span>');
    msgs.appendChild(bot);
    scroll(msgs);
    var body = bot.querySelector(".aspire-chat-body");
    var acc = "";
    var ctl = typeof AbortController !== "undefined" ? new AbortController() : null;
    st.controller = ctl;
    if (status) status.textContent = "";
    function paint() { st.raf = 0; body.innerHTML = md(acc); scroll(msgs); }
    function cancelPaint() { if (st.raf) { cancelAnimationFrame(st.raf); st.raf = 0; } }
    function finish() { st.controller = null; cancelPaint(); lock(p, false); }
    var gen = st.gen;                                        // "New chat" bumps gen: a late event from the old stream is dropped
    function stale() { if (st.gen === gen) return false; cancelPaint(); if (st.controller === ctl) { st.controller = null; lock(p, false); } return true; }
    sport = pickSport(p, cfg, sport);
    stream(apiBase(cfg), { question: q, sport: sport, thread_id: st.thread || null, user_id: userId() }, {
      onThread: function (t) { if (stale()) return;
        if (!t || t === st.thread) return;
        st.thread = t; setStore(p + "-thread", t); persist(p);
      },
      onStatus: function (t) { if (stale()) return; if (status) status.textContent = t; },
      onToken: function (t) { if (stale()) return;
        acc += t;
        if (!st.raf) st.raf = requestAnimationFrame(paint);   // batch: one re-render per frame, not per token
      },
      onDone: function (ev) { if (stale()) return;
        cancelPaint();
        var ans = ev.answer || acc || "(no answer)";
        body.innerHTML = md(ans);
        addActions(bot, ans);
        if (status) status.textContent = (ev.agent ? ev.agent : "") + (ev.tools_used && ev.tools_used.length ? " via " + ev.tools_used.join(", ") : "");
        st.msgs.push({ role: "assistant", text: ans, suggestions: ev.suggestions || [] });
        persist(p);
        ev.thread_id = st.thread;
        setStore(p + "-last", ev);
        finish();
        scroll(msgs);
      },
      onError: function (e) { if (stale()) return;
        bot.replaceWith(errorBubble(String(e)));
        st.msgs.push({ role: "error", text: String(e) });
        persist(p);
        if (status) status.textContent = "";
        finish();
        scroll(msgs);
      },
      onAbort: function () { if (stale()) return;
        cancelPaint();
        body.innerHTML = (acc ? md(acc) : "") + '<div class="aspire-chat-note">Stopped.</div>';
        if (acc) addActions(bot, acc);
        st.msgs.push({ role: "assistant", text: acc, stopped: true });
        persist(p);
        if (status) status.textContent = "Stopped";
        finish();
      },
    }, { signal: ctl ? ctl.signal : undefined });
    return true;
  }

  /* v0.102.0: config.sport SEEDS the picker; only config.lock_sport pins it. An explicit sport (a clarify option
     naming its sport) wins, then the picker's current value, then the seed. */
  function pickSport(p, cfg, explicit) {
    if (cfg && cfg.lock_sport && cfg.sport) return cfg.sport;
    if (explicit) return explicit;
    var sel = el(p, "sport");
    if (sel && sel.value) return sel.value;
    return (cfg && cfg.sport) || null;
  }

  function stop(p) { var st = panel(p); if (st.busy && st.controller) st.controller.abort(); }

  function retry(p, btn) {
    var st = panel(p), msgs = el(p, "messages");
    if (st.busy || !st.lastQ) return;
    var errEl = btn.closest(".aspire-chat-bubble");
    var prev = errEl && errEl.previousElementSibling;
    if (prev && prev.classList.contains("aspire-chat-user")) prev.remove();
    if (errEl) errEl.remove();
    // drop the failed pair from the transcript too
    if (st.msgs.length && st.msgs[st.msgs.length - 1].role === "error") st.msgs.pop();
    if (st.msgs.length && st.msgs[st.msgs.length - 1].role === "user") st.msgs.pop();
    persist(p);
    startSend(p, st.lastQ);
    if (msgs) scroll(msgs);
  }

  function copyText(text, btn) {
    function ok() { if (btn) { var o = btn.textContent; btn.textContent = "Copied"; setTimeout(function () { btn.textContent = o; }, 1200); } }
    function fallback() {
      var ta = document.createElement("textarea");
      ta.value = text; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); ok(); } catch (e) {}
      ta.remove();
    }
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text).then(ok, fallback);
    else fallback();
  }

  /* ---------------------------------------------------------------- delegated listeners */
  function prefixOf(node) {
    var root = node && node.closest ? node.closest(".aspire-chat[data-prefix]") : null;
    return root ? root.getAttribute("data-prefix") : null;
  }
  if (typeof document !== "undefined" && document.addEventListener) {
    document.addEventListener("click", function (e) {
      var t = e.target;
      if (!t || !t.closest) return;
      var p = prefixOf(t);
      if (!p) return;
      var act = t.closest("[data-action]");
      if (act) {
        var a = act.getAttribute("data-action");
        if (a === "stop") { e.preventDefault(); stop(p); }
        else if (a === "retry") { e.preventDefault(); retry(p, act); }
        else if (a === "copy") {
          e.preventDefault();
          var b = act.closest(".aspire-chat-bubble");
          copyText((b && b._raw) || (b ? b.querySelector(".aspire-chat-body").innerText : ""), act);
        }
        return;
      }
      var chip = t.closest("[data-question]");
      if (chip) { e.preventDefault(); startSend(p, chip.getAttribute("data-question")); }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape") return;
      var p = prefixOf(document.activeElement);
      if (p) { if (panel(p).busy) { e.preventDefault(); stop(p); } return; }
      Object.keys(panels).forEach(function (k) { if (panels[k].busy) stop(k); });
    });
  }

  /* ---------------------------------------------------------------- Dash glue */
  var glue = {
    send: function (n_clicks, n_submit, value, sport, thread, config) {
      if (!config) return [nu(), nu()];
      var p = config.prefix, st = panel(p);
      if (!st.config) st.config = config;
      if (st.busy) return [nu(), nu()];                       // refused: a stream is in flight
      if (thread && !st.thread) st.thread = thread;
      return startSend(p, value, sport) ? ["streaming", ""] : [nu(), nu()];
    },
    init: function (config, thread) {
      /* on page load: restore this thread's transcript from sessionStorage, else welcome + "your athletes" chips */
      if (!config) return nu();
      var p = config.prefix, st = panel(p), msgs = el(p, "messages");
      st.config = config;
      if (!thread && config.thread_scope === "session") {
        try { thread = JSON.parse(window.sessionStorage.getItem(p + "-thread") || "null"); } catch (e) { thread = null; }
      }
      st.thread = thread || null;
      st.msgs = loadTranscript(p, st.thread);
      if (msgs) {
        msgs.innerHTML = "";
        if (st.msgs.length) {
          st.msgs.forEach(function (m) { msgs.appendChild(renderMsg(m)); });
          for (var i = st.msgs.length - 1; i >= 0; i--) if (st.msgs[i].role === "user") { st.lastQ = st.msgs[i].text; break; }
          var last = st.msgs[st.msgs.length - 1];
          setStore(p + "-last", { suggestions: (last && last.suggestions) || [], from: "restored" });
          scroll(msgs);
          return nu();
        }
        welcome(p);
      }
      /* M4: on an empty chat, fetch this user's "your athletes" chips; the starters (rendered server-side)
         stay when the engine has none or the call fails */
      var uid = userId();
      if ((config.backend === "engine" && !config.engine_url) || config.backend === "local" || !uid) return nu();
      fetch(apiBase(config) + "/api/agent/chips", {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ user_id: uid }),
      }).then(function (r) { return r.ok ? r.json() : null; }).then(function (d) {
        if (d && d.chips && d.chips.length && !panel(p).msgs.length) setStore(p + "-last", { suggestions: d.chips, from: "user_memory" });
      }).catch(function () {});
      return nu();
    },
    load_chips: function (config) { return glue.init(config, null); },   // pre-0.100 name, kept for callers
    new_chat: function (n, config) {
      /* abort any stream, drop the stored transcript, clear the DOM, show welcome + starters */
      if (!config) return [nu(), nu()];
      var p = config.prefix, st = panel(p), msgs = el(p, "messages"), status = el(p, "status");
      st.config = st.config || config;
      st.gen++;
      if (st.busy && st.controller) st.controller.abort();
      st.controller = null; lock(p, false);
      dropTranscript(p, st.thread);
      st.thread = null; st.msgs = []; st.lastQ = null;
      if (msgs) { msgs.innerHTML = ""; welcome(p); }
      if (status) status.textContent = "";
      return [null, { suggestions: config.starters || [], from: "starters" }];
    },
  };

  window.AspireChat = { stream: stream, md: md, esc: esc, userId: null, version: VERSION, apiBase: apiBase,
                        send: function (prefix, q, sport) { return startSend(prefix, q, sport); }, stop: stop,
                        pickSport: pickSport, _panel: panel };
  window.dash_clientside = window.dash_clientside || {};
  window.dash_clientside.aspire_chat = glue;
})();
