// Node test for aspire-chat.js v0.102.0: sport seed vs lock, JSON-door parsing, clarify reply text.
// Run: node tests/js/chat_v2.test.js   (tests/test_chat_v2.py runs it when node is on PATH)
"use strict";
const fs = require("fs");
const path = require("path");
const assert = require("assert");

const src = fs.readFileSync(path.join(__dirname, "..", "..", "aspire_dash", "assets", "aspire-chat.js"), "utf8");
const nodes = {};
const document = { getElementById: (id) => nodes[id] || null };   // no addEventListener: listeners skipped
const window = {};
new Function("window", "document", src)(window, document);
const A = window.AspireChat;

let n = 0;
function t(name, fn) { fn(); n++; }

t("sport seeds the picker: the picker's current value is sent", () => {
  nodes["p-sport"] = { value: "squash" };
  assert.strictEqual(A.pickSport("p", { sport: "athletics", lock_sport: false }), "squash");
});

t("no picker value falls back to the seed", () => {
  nodes["p-sport"] = { value: "" };
  assert.strictEqual(A.pickSport("p", { sport: "athletics" }), "athletics");
  delete nodes["p-sport"];
  assert.strictEqual(A.pickSport("p", { sport: null }), null);
});

t("lock_sport pins the config sport over the picker and an explicit sport", () => {
  nodes["p-sport"] = { value: "squash" };
  assert.strictEqual(A.pickSport("p", { sport: "athletics", lock_sport: true }), "athletics");
  assert.strictEqual(A.pickSport("p", { sport: "athletics", lock_sport: true }, "padel"), "athletics");
});

t("an explicit sport (clarify option) beats the picker when unlocked", () => {
  nodes["p-sport"] = { value: "squash" };
  assert.strictEqual(A.pickSport("p", { sport: "athletics" }, "padel"), "padel");
});

t("JSON door: a flat /ask payload becomes a done event", () => {
  const ev = A.doneFromJson({ answer: "Which one?", thread_id: "t9", clarify: { question: "Which one?", attr: "sport", options: [] } });
  assert.strictEqual(ev.type, "done");
  assert.strictEqual(ev.answer, "Which one?");
  assert.strictEqual(ev.thread_id, "t9");
  assert.strictEqual(ev.clarify.attr, "sport");
  assert.strictEqual(A.doneFromJson(null), null);
});

t("turnOf keeps the workspace payload and caps spans at 300", () => {
  const spans = Array.from({ length: 350 }, (_, i) => ({ k: "tool", name: "x" + i, t: i, ms: 1 }));
  const turn = A.turnOf({ answer: "a", agent: "g", trace: { spans: spans, spans_dropped: 2 }, clarify: { question: "q" } }, "Q", 1234, "squash");
  assert.strictEqual(turn.q, "Q"); assert.strictEqual(turn.ms, 1234); assert.strictEqual(turn.sport, "squash");
  assert.strictEqual(turn.trace.spans.length, 300); assert.strictEqual(turn.trace.spans_dropped, 52);
  assert.strictEqual(turn.clarify.question, "q");
  assert.strictEqual(spans.length, 350);   // the event itself is not mutated
});

console.log("chat_v2.test.js:" + n + " passed");
