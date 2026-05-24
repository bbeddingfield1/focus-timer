# Focus Timer

A terminal Pomodoro timer with a big ASCII clock, progress bar, and session log.

## Usage

```bash
python3 timer.py
```

Pick a session from the menu:

| Key | Session |
|-----|---------|
| `1` | Work — 25 min |
| `2` | Work — 50 min |
| `3` | Break — 5 min |
| `4` | Break — 15 min |
| `5` | Custom duration |
| `l` | View today's log |
| `q` | Quit |

Press `Ctrl+C` at any time to stop a running session.

## Session Log

Completed sessions are saved to `sessions.json` in the same directory. The log view shows today's Pomodoros, total focused minutes, and a checkmark/cross for each session.

## Requirements

Python 3.6+. No external dependencies.
