import subprocess, sys, threading, time, httpx

AGENT = "http://127.0.0.1:8000"
STATS = {"ok": 0, "fail": 0}


def serve(module, port):
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", f"{module}:app", "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def hit(path, timeout, count=True):
    try:
        httpx.get(f"{AGENT}/run", params={"path": path}, timeout=timeout)
        if count:
            STATS["ok"] += 1
    except Exception:
        if count:
            STATS["fail"] += 1


def bg(fn, *a):
    threading.Thread(target=fn, args=a, daemon=True).start()


def user():
    while True:
        hit("/ok", 5.0)
        time.sleep(1.0)


def row(t):
    m = httpx.get(f"{AGENT}/metrics", timeout=1.0).json()
    h = httpx.get(f"{AGENT}/health", timeout=1.0).status_code
    print(
        f"t={t:02d} busy={m['busy']}/4 queued={m['queued']} "
        f"health={h} ok={STATS['ok']} failed={STATS['fail']}"
    )


procs = [serve("hang_service", 9000), serve("agent", 8000)]
time.sleep(3)
for _ in range(5):
    bg(user)

for t in range(1, 26):
    if t in (6, 12):
        for _ in range(4):
            bg(hit, "/hang", 120.0, False)
    row(t)
    time.sleep(1.0)

for p in procs:
    p.terminate()
