// Node test for aspire-chat.js md(): escape-first, links (http/https only), code, lists, tables.
// Run: node tests/js/md.test.js   (tests/test_chat_panel.py runs it when node is on PATH)
"use strict";
const fs = require("fs");
const path = require("path");
const assert = require("assert");

const src = fs.readFileSync(path.join(__dirname, "..", "..", "aspire_dash", "assets", "aspire-chat.js"), "utf8");
const window = {};
new Function("window", src)(window);   // no document: the delegated listeners are skipped
const md = window.AspireChat.md;

let n = 0;
function t(name, fn) { fn(); n++; }

t("escapes HTML before any markup", () => {
  const h = md('<script>alert(1)</script> <img src=x onerror="y">');
  assert(!h.includes("<script"), h);
  assert(!h.includes("<img"), h);
  assert(h.includes("&lt;script&gt;"), h);
  assert(h.includes("&quot;y&quot;"), h);
});

t("http(s) links become safe anchors", () => {
  const h = md("see [World Athletics](https://worldathletics.org/a_b_c?x=1&y=2)");
  assert(h.includes('<a href="https://worldathletics.org/a_b_c?x=1&amp;y=2" target="_blank" rel="noopener noreferrer">World Athletics</a>'), h);
});

t("javascript: and data: links stay text", () => {
  const h = md("[x](javascript:alert(1)) [y](data:text/html,hi)");
  assert(!h.includes("<a "), h);
});

t("a link text cannot break out of the attribute", () => {
  const h = md('[a](https://e.test/"onmouseover="x)');
  assert(!/href="[^"]*"onmouseover/.test(h), h);
});

t("inline code, bold, italics", () => {
  const h = md("use `a<b` then **bold** and *it* and _it2_ but snake_case_name stays");
  assert(h.includes("<code>a&lt;b</code>"), h);
  assert(h.includes("<strong>bold</strong>"), h);
  assert(h.includes("<em>it</em>") && h.includes("<em>it2</em>"), h);
  assert(h.includes("snake_case_name"), h);
});

t("fenced code block is verbatim and escaped", () => {
  const h = md("before\n```python\nx = 1 < 2\n**not bold**\n```\nafter");
  assert(h.includes('<pre class="aspire-chat-code"><code>x = 1 &lt; 2\n**not bold**</code></pre>'), h);
  assert(h.includes("<p>after</p>"), h);
});

t("unclosed fence while streaming still renders", () => {
  assert(md("```\npartial").includes("<code>partial</code>"));
});

t("ordered and unordered lists", () => {
  const h = md("1. one\n2. two\n\n- a\n- b");
  assert(h.includes("<ol><li>one</li><li>two</li></ol>"), h);
  assert(h.includes("<ul><li>a</li><li>b</li></ul>"), h);
});

t("table gets scroll wrapper, thead and tbody", () => {
  const h = md("| Name | PB |\n|---|---|\n| A | 10.1 |\n| B | **10.2** |");
  assert(h.startsWith('<div class="aspire-chat-table-wrap"><table'), h);
  assert(h.includes("<thead><tr><th>Name</th><th>PB</th></tr></thead>"), h);
  assert(h.includes("<tbody><tr><td>A</td><td>10.1</td></tr><tr><td>B</td><td><strong>10.2</strong></td></tr></tbody>"), h);
});

t("headings", () => {
  assert(md("## Summary").includes("<h5>Summary</h5>"));
});

console.log("md.test.js: " + n + " passed");
