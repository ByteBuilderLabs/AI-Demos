import os, random, sqlite3, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
import tools  # creates shop.db and the charges table before any run starts


def interrupt(cmd, i):
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL)
    try:
        proc.wait(
            timeout=random.Random(i).uniform(1.0, 6.0)
        )  # run i dies at the same moment in both arms
    except subprocess.TimeoutExpired:
        proc.kill()  # SIGKILL on Linux and macOS, TerminateProcess on Windows
    return proc.wait() != 0  # nonzero exit means we killed it


def resume(cmd):
    return subprocess.run(cmd, capture_output=True, timeout=120).returncode == 0


def charges(run_id):
    return (
        sqlite3.connect("shop.db")
        .execute("SELECT COUNT(*) FROM charges WHERE run_id = ?", (run_id,))
        .fetchone()[0]
    )


def trial(i, arm):
    run_id = f"{arm}-{i:03d}"
    cmd = [sys.executable, "agent.py", run_id, arm]
    killed = interrupt(cmd, i)
    gap = (
        charges(run_id) > 0
        and "charge_id"
        not in open(os.path.join("checkpoints", f"{run_id}.json")).read()
    )
    done = resume(cmd)
    return {"killed": killed, "gap": gap, "done": done, "dupes": charges(run_id) > 1}


if __name__ == "__main__":
    with ThreadPoolExecutor(8) as pool:
        rows = list(pool.map(trial, range(100), [sys.argv[1]] * 100))
    print({k: sum(r[k] for r in rows) for k in rows[0]})
