"""R4 browser smoke for the chat panel (checklist 52, slice 1). Not collected by pytest (no test_ prefix).

    .venv/Scripts/python tests/smoke/chat_smoke.py

Starts tests/smoke/chat_demo.py on a free port, drives it with Playwright Chromium at 1280px and 390px,
prints one PASS/FAIL line per check and writes screenshots to tests/smoke/_shots/ (untracked).
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
SHOTS = os.path.join(HERE, "_shots")
os.makedirs(SHOTS, exist_ok=True)
RESULTS: list[tuple[str, str, bool, str]] = []


def free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def count(base) -> int:
    return json.load(urllib.request.urlopen(base + "/_smoke/count"))["count"]


def check(vp, name, ok, detail=""):
    RESULTS.append((vp, name, bool(ok), detail))
    print(f"[{vp}] {'PASS' if ok else 'FAIL'} {name} {detail}", flush=True)


def wait_idle(page, timeout=20000):
    page.wait_for_function("() => !document.getElementById('demo-send').disabled", timeout=timeout)


def run(vp, width, height, base, pw):
    try:
        browser = pw.chromium.launch(channel="chrome")       # installed Chrome: no browser download needed
    except Exception:
        browser = pw.chromium.launch()
    ctx = browser.new_context(viewport={"width": width, "height": height})
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(base, wait_until="networkidle")
    page.wait_for_selector("#demo-input")
    page.wait_for_selector(".aspire-chat-welcome", timeout=10000)
    starters = page.locator("#demo-chips [data-question]").count()
    check(vp, "empty state: welcome + starters", starters == 2, f"starters={starters}")
    page.screenshot(path=os.path.join(SHOTS, f"{vp}_0_empty.png"), full_page=True)

    # 1+2. stream renders; Enter mashed during the stream does not start a second stream
    c0 = count(base)
    inp = page.locator("#demo-input")
    inp.fill("Who are Qatar's top 100m sprinters?")
    inp.press("Enter")
    page.wait_for_function("() => document.getElementById('demo-send').disabled", timeout=5000)
    readonly = page.evaluate("() => document.getElementById('demo-input').readOnly")
    stop_visible = page.locator("#demo-stop").is_visible()
    for _ in range(4):
        inp.press("Enter")
    page.locator("#demo-send").click(force=True)
    wait_idle(page)
    c1 = count(base)
    users = page.locator(".aspire-chat-user").count()
    check(vp, "Enter/Send during stream refused", c1 - c0 == 1 and users == 1 and readonly and stop_visible,
          f"streams={c1 - c0} user_bubbles={users} readonly={readonly} stop_shown={stop_visible}")
    bot = page.locator(".aspire-chat-assistant").last
    has_table = bot.locator(".aspire-chat-table-wrap table thead th").count() == 6
    link = bot.locator("a[href='https://worldathletics.org/']")
    link_ok = link.count() == 1 and link.get_attribute("target") == "_blank" and "noopener" in (link.get_attribute("rel") or "")
    code_ok = bot.locator("pre.aspire-chat-code").count() == 1 and bot.locator("ol li").count() == 2
    copy_ok = bot.locator("[data-action=copy]").count() == 1
    check(vp, "stream renders markdown (table, link, code, list, Copy)", has_table and link_ok and code_ok and copy_ok,
          f"table={has_table} link={link_ok} code+ol={code_ok} copy={copy_ok}")
    page.screenshot(path=os.path.join(SHOTS, f"{vp}_1_answer.png"), full_page=True)

    # 3. chips (from the done event's suggestions) click -> new question streamed
    page.wait_for_selector("#demo-chips [data-question='Compare Athlete A and Athlete B']", timeout=5000)
    c0 = count(base)
    page.locator("#demo-chips [data-question='Compare Athlete A and Athlete B']").click()
    wait_idle(page)
    last_user = page.locator(".aspire-chat-user").last.inner_text()
    check(vp, "chip click sends its question", count(base) - c0 == 1 and last_user == "Compare Athlete A and Athlete B",
          f"last_user={last_user!r}")

    # 4. Stop button, then Esc
    inp.fill("slow answer please")
    inp.press("Enter")
    page.wait_for_selector("#demo-stop:not([hidden])", timeout=5000)
    page.wait_for_timeout(600)
    page.locator("#demo-stop").click()
    page.wait_for_selector(".aspire-chat-assistant >> text=Stopped.", timeout=5000)
    wait_idle(page, 5000)
    unlocked = not page.evaluate("() => document.getElementById('demo-input').readOnly")
    check(vp, "Stop button aborts + unlocks", unlocked and page.locator("#demo-stop").is_hidden(), f"unlocked={unlocked}")
    inp.fill("slow again")
    inp.press("Enter")
    page.wait_for_function("() => document.getElementById('demo-send').disabled", timeout=5000)
    page.wait_for_timeout(400)
    page.keyboard.press("Escape")
    wait_idle(page, 5000)
    stopped = page.locator(".aspire-chat-note", has_text="Stopped.").count()
    check(vp, "Esc aborts", stopped == 2, f"stopped_notes={stopped}")

    # 7. error bubble + Retry (fake fails the first time, answers on retry)
    inp.fill("flaky question " + vp)
    inp.press("Enter")
    page.wait_for_selector(".aspire-chat-error [data-action=retry]", timeout=5000)
    page.screenshot(path=os.path.join(SHOTS, f"{vp}_2_error.png"), full_page=True)
    page.locator(".aspire-chat-error [data-action=retry]").click()
    wait_idle(page)
    errs = page.locator(".aspire-chat-error").count()
    last_user = page.locator(".aspire-chat-user").last.inner_text()
    check(vp, "error bubble + Retry re-sends", errs == 0 and last_user == "flaky question " + vp,
          f"errors_left={errs} last_user={last_user!r}")

    # 5. reload restores the transcript
    before = page.locator(".aspire-chat-bubble").count()
    texts_before = page.locator(".aspire-chat-user").all_inner_texts()
    page.reload(wait_until="networkidle")
    page.wait_for_selector(".aspire-chat-bubble", timeout=10000)
    after = page.locator(".aspire-chat-bubble").count()
    texts_after = page.locator(".aspire-chat-user").all_inner_texts()
    tables = page.locator(".aspire-chat-table-wrap").count()
    check(vp, "reload restores transcript", before == after and texts_before == texts_after and tables >= 1,
          f"bubbles {before}->{after} tables={tables}")

    # 6. no horizontal page overflow (most relevant on mobile; the table scrolls inside its wrapper)
    ov = page.evaluate("() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]")
    wrap = page.evaluate("() => { const w = document.querySelector('.aspire-chat-table-wrap'); return w ? [w.scrollWidth, w.clientWidth] : null; }")
    check(vp, "no horizontal page overflow", ov[0] <= ov[1], f"scrollWidth={ov[0]} clientWidth={ov[1]} table_wrap={wrap}")
    page.screenshot(path=os.path.join(SHOTS, f"{vp}_3_reloaded.png"), full_page=True)

    # dark mode look (html.dark, as dark_mode.js sets it)
    page.evaluate("() => document.documentElement.classList.add('dark')")
    page.screenshot(path=os.path.join(SHOTS, f"{vp}_4_dark.png"), full_page=True)
    page.evaluate("() => document.documentElement.classList.remove('dark')")

    # New chat clears DOM + sessionStorage transcript, starters return
    page.locator("#demo-new-chat").click()
    page.wait_for_selector(".aspire-chat-welcome", timeout=5000)
    page.wait_for_function("() => document.querySelectorAll('#demo-chips [data-question]').length === 2", timeout=5000)
    keys = page.evaluate("() => Object.keys(sessionStorage).filter(k => k.startsWith('aspire-chat:'))")
    bubbles = page.locator(".aspire-chat-bubble").count()
    page.reload(wait_until="networkidle")
    page.wait_for_selector(".aspire-chat-welcome", timeout=10000)
    bubbles_reload = page.locator(".aspire-chat-bubble").count()
    check(vp, "New chat clears transcript + storage", bubbles == 0 and keys == [] and bubbles_reload == 0,
          f"bubbles={bubbles} stored_keys={keys} after_reload={bubbles_reload}")
    check(vp, "no page JS errors", not errors, "; ".join(errors)[:300])
    browser.close()


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    port = free_port()
    env = dict(os.environ, CHAT_DEMO_PORT=str(port))
    proc = subprocess.Popen([sys.executable, os.path.join(HERE, "chat_demo.py"), str(port)], env=env,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = f"http://127.0.0.1:{port}"
    try:
        for _ in range(60):
            try:
                urllib.request.urlopen(base + "/_smoke/count", timeout=1)
                break
            except Exception:
                time.sleep(0.5)
        with sync_playwright() as pw:
            for vp, w, h in (("desktop", 1280, 900), ("mobile", 390, 844)):
                try:
                    run(vp, w, h, base, pw)
                except Exception as e:  # report and carry on to the other viewport
                    check(vp, "run completed", False, repr(e)[:400])
    finally:
        proc.terminate()
    failed = [r for r in RESULTS if not r[2]]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed; screenshots in {SHOTS}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
