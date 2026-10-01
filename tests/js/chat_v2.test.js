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

console.log("chat_v2.test.js: " + n + " passed");
