#!/usr/bin/env python3
"""A simple Pomodoro timer — web-based, zero dependencies."""

import json
import subprocess
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import webbrowser

STATS_FILE = Path.home() / ".pomodoro-stats.json"
WORK_DURATION = 25 * 60
BREAK_DURATION = 5 * 60
PORT = 9876


def load_stats():
    if STATS_FILE.exists():
        try:
            return json.loads(STATS_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_stats(stats):
    STATS_FILE.write_text(json.dumps(stats, ensure_ascii=False, indent=2))


def notify(title, message):
    script = f'display notification "{message}" with title "{title}"'
    subprocess.run(["osascript", "-e", script], check=False)


HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pomodoro Timer</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #1a1a2e; color: #eee; min-height: 100vh;
    display: flex; justify-content: center; align-items: center;
  }
  .container {
    width: 360px; background: #16213e; border-radius: 16px;
    padding: 32px 24px; box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  }
  h1 { text-align: center; font-size: 20px; margin-bottom: 24px; color: #e94560; }
  .timer {
    text-align: center; font-size: 72px; font-weight: 700;
    font-variant-numeric: tabular-nums; margin: 16px 0;
    color: #0f3460; background: #e94560; border-radius: 12px;
    padding: 8px 0;
  }
  .timer.break-mode { background: #0f3460; color: #e94560; }
  .status {
    text-align: center; font-size: 14px; color: #aaa;
    margin-bottom: 20px; height: 20px;
  }
  .task-input {
    display: flex; gap: 8px; margin-bottom: 16px;
  }
  .task-input input {
    flex: 1; padding: 8px 12px; border: 1px solid #333;
    border-radius: 8px; background: #0f3460; color: #eee;
    font-size: 14px; outline: none;
  }
  .task-input input:focus { border-color: #e94560; }
  .buttons {
    display: flex; gap: 8px; justify-content: center; margin-bottom: 24px;
  }
  .buttons button {
    padding: 10px 20px; border: none; border-radius: 8px;
    font-size: 14px; cursor: pointer; font-weight: 600;
    transition: opacity 0.15s;
  }
  .buttons button:hover { opacity: 0.85; }
  .buttons button:disabled { opacity: 0.4; cursor: default; }
  .btn-start { background: #e94560; color: #fff; }
  .btn-pause { background: #f5a623; color: #fff; }
  .btn-reset { background: #333; color: #ccc; }
  .btn-skip { background: #0f3460; color: #ccc; }
  .stats { border-top: 1px solid #333; padding-top: 16px; }
  .stats h2 { font-size: 14px; color: #aaa; margin-bottom: 8px; }
  .stats-list { font-size: 13px; color: #ccc; line-height: 1.8; }
  .stats-count { font-size: 16px; font-weight: 700; color: #e94560; margin-bottom: 4px; }
  .stats-item { display: flex; gap: 8px; }
  .stats-time { color: #888; min-width: 44px; }
</style>
</head>
<body>
<div class="container">
  <h1>Pomodoro Timer</h1>
  <div class="timer" id="timer">25:00</div>
  <div class="status" id="status">Ready</div>
  <div class="task-input">
    <input type="text" id="taskInput" placeholder="What are you working on?" autofocus>
  </div>
  <div class="buttons">
    <button class="btn-start" id="startBtn" onclick="start()">Start</button>
    <button class="btn-pause" id="pauseBtn" onclick="pause()" disabled>Pause</button>
    <button class="btn-reset" id="resetBtn" onclick="reset()">Reset</button>
    <button class="btn-skip" id="skipBtn" onclick="skip()" disabled>Skip</button>
  </div>
  <div class="stats">
    <h2>Today</h2>
    <div id="statsArea" class="stats-list">Loading...</div>
  </div>
</div>
<script>
const WORK = 25 * 60, BREAK = 5 * 60;
let remaining = WORK, isWorking = true, running = false, timer = null;
let sessionStart = null, currentTask = '';

function fmt(s) {
  const m = Math.floor(s / 60), sec = s % 60;
  return String(m).padStart(2,'0') + ':' + String(sec).padStart(2,'0');
}

function updateDisplay() {
  document.getElementById('timer').textContent = fmt(remaining);
  const el = document.getElementById('timer');
  el.className = isWorking ? 'timer' : 'timer break-mode';
  const st = document.getElementById('status');
  if (running) st.textContent = isWorking ? 'Working...' : 'Break time';
  else st.textContent = isWorking ? 'Ready' : 'Break';
}

function start() {
  if (running) return;
  running = true;
  sessionStart = new Date();
  currentTask = document.getElementById('taskInput').value.trim() || 'No task';
  document.getElementById('startBtn').disabled = true;
  document.getElementById('pauseBtn').disabled = false;
  document.getElementById('skipBtn').disabled = false;
  tick();
}

function pause() {
  running = false;
  clearInterval(timer);
  document.getElementById('startBtn').disabled = false;
  document.getElementById('pauseBtn').disabled = true;
}

function reset() {
  running = false;
  clearInterval(timer);
  isWorking = true;
  remaining = WORK;
  sessionStart = null;
  document.getElementById('startBtn').disabled = false;
  document.getElementById('pauseBtn').disabled = true;
  document.getElementById('skipBtn').disabled = true;
  updateDisplay();
}

function skip() {
  clearInterval(timer);
  running = false;
  onPhaseEnd();
}

function tick() {
  timer = setInterval(() => {
    remaining--;
    updateDisplay();
    if (remaining <= 0) {
      clearInterval(timer);
      running = false;
      onPhaseEnd();
    }
  }, 1000);
}

function onPhaseEnd() {
  if (isWorking) {
    recordPomodoro();
    notify('Pomodoro Done', 'Take a 5-minute break! (' + currentTask + ')');
    isWorking = false;
    remaining = BREAK;
  } else {
    notify('Break Over', 'Time to start the next pomodoro!');
    isWorking = true;
    remaining = WORK;
    document.getElementById('taskInput').value = '';
  }
  document.getElementById('startBtn').disabled = false;
  document.getElementById('pauseBtn').disabled = true;
  document.getElementById('skipBtn').disabled = true;
  updateDisplay();
  loadStats();
}

function recordPomodoro() {
  const time = sessionStart ?
    String(sessionStart.getHours()).padStart(2,'0') + ':' +
    String(sessionStart.getMinutes()).padStart(2,'0') : '??';
  fetch('/api/record', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({task: currentTask, time: time})
  });
}

function notify(title, msg) {
  fetch('/api/notify', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({title: title, message: msg})
  });
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification(title, {body: msg});
  }
}

function loadStats() {
  fetch('/api/stats').then(r => r.json()).then(data => {
    const area = document.getElementById('statsArea');
    if (!data.length) { area.innerHTML = 'No pomodoros yet today.'; return; }
    area.innerHTML = '<div class="stats-count">Completed: ' + data.length + ' pomodoro(s)</div>' +
      data.map((e, i) =>
        '<div class="stats-item"><span class="stats-time">' + e.time + '</span><span>' + e.task + ' (' + e.duration + 'm)</span></div>'
      ).join('');
  });
}

// Request notification permission
if ('Notification' in window && Notification.permission === 'default') {
  Notification.requestPermission();
}

updateDisplay();
loadStats();
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress logs

    def do_GET(self):
        if self.path == '/api/stats':
            self._handle_stats()
        else:
            self._serve_html()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length)) if length else {}
        if self.path == '/api/record':
            self._handle_record(body)
        elif self.path == '/api/notify':
            self._handle_notify(body)
        self._json_response({"ok": True})

    def _serve_html(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML.encode())

    def _handle_stats(self):
        stats = load_stats()
        today = stats.get(datetime.now().strftime("%Y-%m-%d"), [])
        self._json_response(today)

    def _handle_record(self, body):
        stats = load_stats()
        today_key = datetime.now().strftime("%Y-%m-%d")
        today = stats.setdefault(today_key, [])
        today.append({"task": body.get("task", "No task"),
                      "duration": WORK_DURATION // 60,
                      "time": body.get("time", "??")})
        save_stats(stats)

    def _handle_notify(self, body):
        notify(body.get("title", "Pomodoro"), body.get("message", ""))

    def _json_response(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())


def main():
    server = HTTPServer(('127.0.0.1', PORT), Handler)
    url = f'http://127.0.0.1:{PORT}'
    print(f'Pomodoro Timer running at {url}')
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nBye!')
        server.server_close()


if __name__ == '__main__':
    main()
