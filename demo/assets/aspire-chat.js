/* aspire-chat.js (M7, 2026-08-30): the Aspire sports chatbot client for any web page.
   Plain JS, no build step. Two uses:
     1. window.AspireChat.stream(engineUrl, {question, sport, thread_id}, {onToken, onStatus, onDone, onError})
        for React/Next/vanilla pages (POST {engineUrl}/api/agent/ask/stream, Server-Sent Events).
     2. window.dash_clientside.aspire_chat.* : the Dash glue used by aspire_dash.components.chat_panel.
   SSE lines are `data: <json>` with type in thread | status | token | done | error. */
(function () {
  "use strict";

  async function stream(engineUrl, body, handlers) {
    handlers = handlers || {};
    var res;
    try {
      res = await fetch(engineUrl.replace(/\/$/, "") + "/api/agent/ask/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
        body: JSON.stringify(body),
      });
    } catch (e) {
      if (handlers.onError) handlers.onError("network: " + e);
      return null;
    }
    if (!res.ok || !res.body) {
      if (handlers.onError) handlers.onError("HTTP " + res.status);
      return null;
    }
    var reader = res.body.getReader();
    var dec = new TextDecoder();
    var buf = "";
    var done = null;
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
        else if (ev.type === "token" && handlers.onToken) handlers.onToken(ev.text || "");
        else if (ev.type === "status" && handlers.onStatus) handlers.onStatus(ev.text || ev.node || "");
        else if (ev.type === "done") { done = ev; if (handlers.onDone) handlers.onDone(ev); }
        else if (ev.type === "error" && handlers.onError) handlers.onError(ev.error || "engine error");
      }
    }
    return done;
  }

  /* minimal markdown for the streamed answer: bold, headings, tables and paragraphs. The done event's full
     answer is re-rendered the same way, so what the coach reads is the engine's markdown, lightly typeset. */
  function esc(s) { return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
  function md(text) {
    var lines = esc(text || "").split("\n");
    var html = [], inTable = false;
    for (var i = 0; i < lines.length; i++) {
      var l = lines[i];
      if (/^\s*\|.*\|\s*$/.test(l)) {
        if (/^\s*\|[\s\-:|]+\|\s*$/.test(l)) continue;
        var cells = l.trim().replace(/^\||\|$/g, "").split("|").map(function (c) { return c.trim(); });
        if (!inTable) { html.push('<table class="table table-sm aspire-chat-table"><tr>' + cells.map(function (c) { return "<th>" + c + "</th>"; }).join("") + "</tr>"); inTable = true; }
        else html.push("<tr>" + cells.map(function (c) { return "<td>" + c + "</td>"; }).join("") + "</tr>");
        continue;
      }
      if (inTable) { html.push("</table>"); inTable = false; }
      if (/^###\s/.test(l)) html.push("<h6>" + l.replace(/^###\s/, "") + "</h6>");
      else if (/^##\s/.test(l)) html.push("<h5>" + l.replace(/^##\s/, "") + "</h5>");
      else if (/^[-*]\s/.test(l)) html.push("<div>&bull; " + l.replace(/^[-*]\s/, "") + "</div>");
      else if (l.trim() === "") html.push("<div style=\"height:6px\"></div>");
      else html.push("<div>" + l + "</div>");
    }
    if (inTable) html.push("</table>");
    return html.join("").replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/`([^`]+)`/g, "<code>$1</code>");
  }

  function bubble(role, inner) {
    var d = document.createElement("div");
    d.className = "aspire-chat-bubble aspire-chat-" + role;
    d.style.cssText = role === "user"
      ? "margin:6px 0 6px auto;max-width:85%;background:#004185;color:#fff;border-radius:12px;padding:8px 12px;width:fit-content"
      : "margin:6px auto 6px 0;max-width:95%;background:#f3f5f8;border-radius:12px;padding:8px 12px;width:fit-content";
    d.innerHTML = inner;
    return d;
  }

  /* M4: a stable anonymous user id per browser (localStorage) so the engine can remember this coach's athletes
     across threads and sessions; apps with a login can set window.AspireChat.userId instead. */
  function userId() {
    if (window.AspireChat && window.AspireChat.userId) return window.AspireChat.userId;
    try {
      var k = "aspire-chat-user", v = localStorage.getItem(k);
      if (!v) { v = "anon-" + Math.random().toString(36).slice(2, 10) + Date.now().toString(36); localStorage.setItem(k, v); }
      return v;
    } catch (e) { return null; }
  }

  function setStore(id, data) {
    /* write a dcc.Store from JS via dash_clientside.set_props (Dash >= 2.16) */
    if (window.dash_clientside && window.dash_clientside.set_props) window.dash_clientside.set_props(id, { data: data });
  }

  var glue = {
    send: function (n_clicks, n_submit, value, sport, thread, config) {
      var q = (value || "").trim();
      if (!q || !config) return window.dash_clientside.no_update;
      var p = config.prefix;
      var msgs = document.getElementById(p + "-messages");
      var status = document.getElementById(p + "-status");
      var input = document.getElementById(p + "-input");
      var sendBtn = document.getElementById(p + "-send");
      if (!msgs) return window.dash_clientside.no_update;
      msgs.appendChild(bubble("user", esc(q)));
      var bot = bubble("assistant", "<span class=\"text-muted\">thinking...</span>");
      msgs.appendChild(bot);
      msgs.scrollTop = msgs.scrollHeight;
      if (input) input.value = "";
      if (sendBtn) sendBtn.disabled = true;
      var acc = "";
      var threadId = thread;
      stream(config.engine_url, { question: q, sport: config.sport || sport || null, thread_id: threadId || null, user_id: userId() }, {
        onThread: function (t) { threadId = t; setStore(p + "-thread", t); },
        onStatus: function (t) { if (status) status.textContent = t; },
        onToken: function (t) { acc += t; bot.innerHTML = md(acc); msgs.scrollTop = msgs.scrollHeight; },
        onDone: function (ev) {
          bot.innerHTML = md(ev.answer || acc || "(no answer)");
          if (status) status.textContent = (ev.agent ? ev.agent : "") + (ev.tools_used && ev.tools_used.length ? " via " + ev.tools_used.join(", ") : "");
          ev.thread_id = threadId;
          setStore(p + "-last", ev);
          if (sendBtn) sendBtn.disabled = false;
          msgs.scrollTop = msgs.scrollHeight;
        },
        onError: function (e) {
          bot.innerHTML = "<span class=\"text-danger\">" + esc(String(e)) + "</span>";
          if (sendBtn) sendBtn.disabled = false;
        },
      });
      return "streaming";
    },
    load_chips: function (config) {
      /* M4: on an empty chat, fetch this user's "your athletes" chips and hand them to the last-event store */
      if (!config || !config.engine_url) return window.dash_clientside.no_update;
      var p = config.prefix, uid = userId();
      if (!uid) return window.dash_clientside.no_update;
      fetch(config.engine_url.replace(/\/$/, "") + "/api/agent/chips", {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ user_id: uid }),
      }).then(function (r) { return r.ok ? r.json() : null; }).then(function (d) {
        if (d && d.chips && d.chips.length) setStore(p + "-last", { suggestions: d.chips, from: "user_memory" });
      }).catch(function () {});
      return window.dash_clientside.no_update;
    },
    chip_click: function (n_clicks, config) {
      /* a chip carries its question in data-question; put it in the input and submit */
      var t = window.dash_clientside.callback_context && window.dash_clientside.callback_context.triggered;
      var el = document.activeElement;
      var q = el && el.getAttribute ? el.getAttribute("data-question") : null;
      if (!q) return window.dash_clientside.no_update;
      var p = config && config.prefix;
      var sendBtn = p && document.getElementById(p + "-send");
      setTimeout(function () { if (sendBtn) sendBtn.click(); }, 50);
      return q;
    },
  };

  window.AspireChat = { stream: stream, md: md, userId: null, version: "0.75.1" };
  window.dash_clientside = window.dash_clientside || {};
  window.dash_clientside.aspire_chat = glue;
})();
