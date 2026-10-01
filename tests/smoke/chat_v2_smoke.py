"""R4 browser smoke for chat_panel v0.102.0 (not collected by pytest: no test_ prefix).

    .venv/Scripts/python tests/smoke/chat_v2_smoke.py [shots_dir]

Starts tests/smoke/chat_demo.py (relay mode under /content/abc/ + the fake engine) and drives it with Playwright
Chromium at 1440x900 and 390x844: ask -> streamed answer -> Tables tab (data_table + medals) -> Charts tab ->
Trace tab (waterfall rows incl. node rows) -> "Ali" gets a clarify question -> clicking the Squash chip sends
"Squash (aspire_id 4242)" with sport squash on the SAME thread -> reload restores turns (Trace still there) ->
sport picker: the user's pick is what the engine receives. Checks no horizontal overflow at both widths.
Prints one PASS/FAIL line per check; exit code 1 on any FAIL.
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import urllib.request

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "_shots")
os.makedirs(SHOTS, exist_ok=True)
RESULTS = []


def free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def check(vp, name, ok, detail=""):
    RESULTS.append(bool(ok))
    print(f"[{vp}] {'PASS' if ok else 'FAIL'} {name} {detail}".rstrip(), flush=True)


def engine(base):
    return json.load(urllib.request.urlopen(base + "/_smoke/count"))


def overflow(page) -> int:
    return page.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")


def tab(page, i):
    """Click tab i (0 Answer, 1 Tables, 2 Charts, 3 Trace) by position: the labels change as counts arrive."""
    page.wait_for_timeout(300)                       # let the turns -> tab labels callback land
    page.click(f"#demo-tabs .tab >> nth={i}")


def run(pw, vp, size, url, ebase):
    browser = pw.chromium.launch()
    ctx = browser.new_context(viewport=size)
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(url)
    page.wait_for_selector("#demo-input")
    idle = "() => !document.getElementById('demo-send').disabled"

    # 1. ask -> streamed answer
    page.fill("#demo-input", "Who are Qatar's top 100m sprinters?")
    page.click("#demo-send")
    page.wait_for_selector(".aspire-chat-assistant .aspire-chat-actions", timeout=20000)
    page.wait_for_function(idle)
    ans = page.inner_text(".aspire-chat-assistant >> nth=-1")
    check(vp, "streamed answer rendered", "Qatar 100m" in ans and "Athlete A" in ans)
    page.screenshot(path=os.path.join(SHOTS, f"chatv2_{vp}_1_answer.png"))
    check(vp, "no horizontal overflow (answer)", overflow(page) <= 0, f"overflow={overflow(page)}")

    # 2. Tables tab: data_table + medals; tab label carries the count
    tab(page, 1)
    page.wait_for_selector("#demo-pane-tables:not([hidden]) .aspire-data-table")
    medals = page.locator("#demo-tables .placement-badge").count()
    label = page.inner_text("#demo-tabs .tab >> nth=1")
    check(vp, "Tables tab: data_table with 3 medals", medals == 3, f"medals={medals} label={label!r}")
    page.screenshot(path=os.path.join(SHOTS, f"chatv2_{vp}_2_tables.png"))
    check(vp, "no horizontal overflow (tables)", overflow(page) <= 0, f"overflow={overflow(page)}")

    # 3. Charts tab
    tab(page, 2)
    page.wait_for_selector("#demo-pane-charts:not([hidden]) .js-plotly-plot", timeout=15000)
    check(vp, "Charts tab: a Plotly chart", page.locator("#demo-charts .js-plotly-plot").count() >= 1)

    # 4. Trace tab: waterfall rows with node rows from trace.spans
    tab(page, 3)
    page.wait_for_selector("#demo-pane-trace:not([hidden]) .aspire-chat-tr-row")
    kinds = page.eval_on_selector_all("#demo-trace .aspire-chat-tr-row", "els => els.map(e => e.dataset.kind)")
    check(vp, "Trace tab: 6 spans incl. 3 node rows", kinds == ["node", "node", "llm", "tool", "tool", "node"], str(kinds))
    widths = page.eval_on_selector_all("#demo-trace .aspire-chat-tr-bar", "els => els.map(e => parseFloat(e.style.width))")
    ratio = widths[1] / widths[2]                    # athletics_agent node 1010 ms vs its model call 610 ms
    check(vp, "Trace bar widths scale with span duration", abs(ratio - 1010 / 610) < 0.01, f"ratio={ratio:.3f}")
    page.screenshot(path=os.path.join(SHOTS, f"chatv2_{vp}_3_trace.png"))
    check(vp, "no horizontal overflow (trace)", overflow(page) <= 0, f"overflow={overflow(page)}")

    # 5. clarify: question -> chips -> click sends the follow-up on the same thread
    tab(page, 0)
    before = engine(ebase)["count"]
    page.fill("#demo-input", "Ali PB")
    page.press("#demo-input", "Enter")
    page.wait_for_selector(".aspire-chat-clarify button", timeout=20000)
    page.wait_for_function(idle)
    opts = page.eval_on_selector_all(".aspire-chat-clarify button", "els => els.map(e => [e.textContent, e.dataset.question, e.dataset.sport])")
    check(vp, "clarify chips rendered", opts == [["Squash", "Squash (aspire_id 4242)", "squash"], ["Padel", "Padel", "padel"]], str(opts))
    page.screenshot(path=os.path.join(SHOTS, f"chatv2_{vp}_4_clarify.png"))
    check(vp, "no horizontal overflow (clarify)", overflow(page) <= 0, f"overflow={overflow(page)}")
    page.click(".aspire-chat-clarify button:has-text('Squash')")
    page.wait_for_function(f"() => document.querySelectorAll('.aspire-chat-user').length >= 3", timeout=10000)
    page.wait_for_function(idle, timeout=20000)
    info = engine(ebase)
    bodies = info["bodies"][before:]
    ok = (len(bodies) == 2 and bodies[1]["question"] == "Squash (aspire_id 4242)" and bodies[1]["sport"] == "squash"
          and bodies[1]["thread_id"] and bodies[1]["thread_id"] == bodies[0]["thread_id"])
    check(vp, "chip click sends the option on the same thread", ok, json.dumps(bodies))
    page.screenshot(path=os.path.join(SHOTS, f"chatv2_{vp}_5_followup.png"))

    # 6. reload restores the turns (the Trace tab shows the last answer's spans again)
    page.reload()
    page.wait_for_selector(".aspire-chat-user")
    tab(page, 3)
    page.wait_for_selector("#demo-pane-trace:not([hidden]) .aspire-chat-tr-row", timeout=10000)
    n = page.locator("#demo-trace .aspire-chat-tr-row").count()
    check(vp, "reload restores turns (trace rows)", n == 6, f"rows={n}")
    tables = page.inner_text("#demo-tabs .tab >> nth=1")
    check(vp, "reload restores turns (tables count)", "(2)" in tables, repr(tables))

    # 7. sport seeds, does not lock: the user's pick reaches the engine
    tab(page, 0)
    page.select_option("#demo-sport", "squash")
    page.fill("#demo-input", "Latest squash results")
    page.click("#demo-send")
    page.wait_for_function(idle, timeout=20000)
    page.wait_for_selector(".aspire-chat-assistant .aspire-chat-actions")
    last = engine(ebase)["bodies"][-1]
    check(vp, "picker value is sent (sport not locked)", last["sport"] == "squash", json.dumps(last))
    check(vp, "no page errors", not errors, "; ".join(errors)[:300])
    browser.close()


def main():
    port, eport = free_port(), free_port()
    log = open(os.path.join(SHOTS, "chatv2_demo.log"), "w")
    proc = subprocess.Popen([sys.executable, os.path.join(HERE, "chat_demo.py"), str(port), str(eport)],
                            stdout=log, stderr=subprocess.STDOUT)
    base, ebase = f"http://127.0.0.1:{port}/content/abc/", f"http://127.0.0.1:{eport}"
    try:
        for _ in range(100):
            try:
                urllib.request.urlopen(base, timeout=1)
                break
            except Exception:  # noqa: BLE001
                time.sleep(0.2)
        with sync_playwright() as pw:
            for vp, size in (("desktop", {"width": 1440, "height": 900}), ("mobile", {"width": 390, "height": 844})):
                run(pw, vp, size, base, ebase)
    finally:
        proc.terminate()
    print(f"{sum(RESULTS)}/{len(RESULTS)} passed")
    sys.exit(0 if all(RESULTS) else 1)


if __name__ == "__main__":
    main()
