#!/usr/bin/env python3
"""Focus Timer — terminal Pomodoro timer with ASCII display and session log."""

import sys
import time
import signal
import os
import json
from datetime import datetime, date

# ── ANSI colors ──────────────────────────────────────────────────────────────
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

# ── Big ASCII digits (5 rows × 3 cols each) ──────────────────────────────────
DIGITS = {
    "0": ["███", "█ █", "█ █", "█ █", "███"],
    "1": [" █ ", "██ ", " █ ", " █ ", "███"],
    "2": ["███", "  █", "███", "█  ", "███"],
    "3": ["███", "  █", "███", "  █", "███"],
    "4": ["█ █", "█ █", "███", "  █", "  █"],
    "5": ["███", "█  ", "███", "  █", "███"],
    "6": ["███", "█  ", "███", "█ █", "███"],
    "7": ["███", "  █", "  █", "  █", "  █"],
    "8": ["███", "█ █", "███", "█ █", "███"],
    "9": ["███", "█ █", "███", "  █", "███"],
    ":": [" ", "▪", " ", "▪", " "],
}

def render_time(seconds: int, color: str) -> str:
    m, s = divmod(seconds, 60)
    chars = f"{m:02d}:{s:02d}"
    rows = [""] * 5
    for ch in chars:
        glyph = DIGITS[ch]
        for i in range(5):
            rows[i] += glyph[i] + "  "
    return "\n".join(color + BOLD + row + RESET for row in rows)

# ── Session log ───────────────────────────────────────────────────────────────
LOG_FILE = os.path.join(os.path.dirname(__file__), "sessions.json")

def load_log() -> dict:
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            return json.load(f)
    return {"sessions": []}

def save_session(kind: str, duration_min: int, completed: bool):
    data = load_log()
    data["sessions"].append({
        "date": str(date.today()),
        "time": datetime.now().strftime("%H:%M"),
        "type": kind,
        "minutes": duration_min,
        "completed": completed,
    })
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def show_log():
    data = load_log()
    sessions = data["sessions"]
    if not sessions:
        print(f"{DIM}No sessions logged yet.{RESET}")
        return
    today = str(date.today())
    today_sessions = [s for s in sessions if s["date"] == today]
    completed_today = sum(1 for s in today_sessions if s["completed"] and s["type"] == "work")
    total_min = sum(s["minutes"] for s in today_sessions if s["completed"] and s["type"] == "work")
    print(f"\n{BOLD}{CYAN}── Today's sessions ({today}) ─────────────────{RESET}")
    for s in today_sessions[-10:]:
        icon = "✓" if s["completed"] else "✗"
        color = GREEN if s["completed"] else DIM
        label = "WORK" if s["type"] == "work" else s["type"].upper()
        print(f"  {color}{icon} {s['time']}  {label:6s}  {s['minutes']} min{RESET}")
    print(f"\n  {BOLD}Pomodoros completed: {completed_today}  ({total_min} min focused){RESET}\n")

# ── Timer core ────────────────────────────────────────────────────────────────
interrupted = False

def handle_sigint(sig, frame):
    global interrupted
    interrupted = True

def clear():
    os.system("clear" if os.name == "posix" else "cls")

def countdown(label: str, total_sec: int, color: str) -> bool:
    """Returns True if completed, False if interrupted."""
    global interrupted
    interrupted = False
    signal.signal(signal.SIGINT, handle_sigint)
    start = time.monotonic()

    while True:
        elapsed = time.monotonic() - start
        remaining = max(0, total_sec - int(elapsed))
        clear()
        print(f"\n  {BOLD}{color}{label}{RESET}\n")
        print("  " + render_time(remaining, color).replace("\n", "\n  "))
        pct = (total_sec - remaining) / total_sec
        bar_len = 36
        filled = int(bar_len * pct)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"\n  {color}{bar}{RESET}  {DIM}{int(pct*100)}%{RESET}")
        print(f"\n  {DIM}Press Ctrl+C to stop{RESET}")

        if remaining == 0:
            break
        if interrupted:
            clear()
            print(f"\n  {YELLOW}Session interrupted.{RESET}\n")
            return False
        time.sleep(0.25)

    clear()
    print(f"\n  {BOLD}{GREEN}✓  {label} complete!{RESET}\n")
    time.sleep(1)
    return True

def bell():
    sys.stdout.write("\a")
    sys.stdout.flush()

# ── Main menu ─────────────────────────────────────────────────────────────────
CONFIGS = {
    "1": ("Work — 25 min",  25 * 60, "work",  CYAN),
    "2": ("Work — 50 min",  50 * 60, "work",  CYAN),
    "3": ("Break — 5 min",   5 * 60, "break", GREEN),
    "4": ("Break — 15 min", 15 * 60, "break", GREEN),
    "5": ("Custom",          0,       "work",  YELLOW),
}

def menu():
    clear()
    print(f"\n  {BOLD}{CYAN}Focus Timer{RESET}  {DIM}Pomodoro for the terminal{RESET}\n")
    for key, (label, _, _, _) in CONFIGS.items():
        print(f"  {BOLD}{key}{RESET}  {label}")
    print(f"\n  {BOLD}l{RESET}  View today's log")
    print(f"  {BOLD}q{RESET}  Quit\n")

def prompt(msg: str) -> str:
    try:
        return input(f"  {BOLD}{msg}{RESET} ").strip()
    except (EOFError, KeyboardInterrupt):
        return "q"

def run():
    pomodoro_count = 0

    while True:
        menu()
        choice = prompt("›")

        if choice == "q":
            clear()
            print(f"\n  {DIM}Goodbye. Stay focused!{RESET}\n")
            break

        if choice == "l":
            clear()
            show_log()
            prompt("Press Enter to continue")
            continue

        if choice not in CONFIGS:
            continue

        label, duration, kind, color = CONFIGS[choice]

        if choice == "5":
            raw = prompt("Minutes:")
            if not raw.isdigit() or int(raw) <= 0:
                continue
            duration = int(raw) * 60
            label = f"Custom — {raw} min"

        completed = countdown(label, duration, color)
        bell()
        save_session(kind, duration // 60, completed)

        if completed and kind == "work":
            pomodoro_count += 1
            print(f"  {BOLD}{GREEN}Pomodoro #{pomodoro_count} logged.{RESET}")
            if pomodoro_count % 4 == 0:
                print(f"  {BOLD}{YELLOW}Nice work! Time for a long break.{RESET}\n")
            else:
                print(f"  {DIM}Tip: take a short break before the next session.{RESET}\n")
            time.sleep(1.5)

if __name__ == "__main__":
    run()
