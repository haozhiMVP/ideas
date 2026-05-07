# Pomodoro Timer

A simple Pomodoro timer — web-based, zero dependencies.

## Features

- 25-minute work / 5-minute break cycle
- Task labels for each pomodoro session
- Daily statistics tracking
- macOS system notifications
- Start / Pause / Reset / Skip controls

## Usage

```bash
python3 pomodoro.py
```

No dependencies required — uses Python's built-in `http.server`. Opens in your default browser.

## Stats

Statistics are saved to `~/.pomodoro-stats.json` in this format:

```json
{
  "2026-05-07": [
    {"task": "Write login page", "duration": 25, "time": "10:00"},
    {"task": "Fix bug #123", "duration": 25, "time": "10:30"}
  ]
}
```

## Requirements

- Python 3.10+
- macOS (for system notifications)
