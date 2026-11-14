import json, logging, sys, time
from concurrent.futures import ThreadPoolExecutor
from agent import ask, cache, CACHE, tokens_used
from context import ARMS
from dataset import QUESTIONS, make_conversation, grade

LENGTHS, POSITIONS, REPEATS = [5, 15, 30, 50], ["early", "middle", "late"], 1
WORKERS = 8  # parallel API calls: lower it if you keep hitting rate limits


class Trap(logging.Handler):
    count = 0

    def emit(self, record):
        self.count += 1  # logging holds a lock here, so threads are safe


logging.basicConfig(format="%(levelname)s %(name)s: %(message)s")  # print it too
trap = Trap(level=logging.WARNING)
logging.getLogger().addHandler(trap)  # every library logger propagates up here
logging.captureWarnings(True)  # Python warnings become log records too


SYSTEM = "You are a helpful assistant. Answer using the conversation."  # frozen


def run_one(q, n_turns, position, seed, build_payload):
    history = [{"role": "system", "content": SYSTEM}]
    history += make_conversation(n_turns, position, q, seed)  # fact planted here
    try:
        reply, payload = ask(
            history, q["question"], build_payload, must_keep=[q["answer"]]
        )
    except AssertionError as err:  # nothing raises this yet. Hold that thought.
        logging.error("context loss: %s", err)
        return False, True, True  # wrong, fact gone, loud
    seen = " ".join(m["content"] for m in payload)
    return grade(q, reply), q["answer"] not in seen, False  # correct, fact gone, loud


def sweep(build_payload, label):
    start = time.perf_counter()
    with ThreadPoolExecutor(WORKERS) as pool:
        for n in LENGTHS:
            for pos in POSITIONS:
                jobs = [
                    (q, n, pos, s, build_payload)
                    for q in QUESTIONS
                    for s in range(REPEATS)
                ]
                runs = list(pool.map(lambda job: run_one(*job), jobs))
                acc, gone, loud = (
                    sum(r[i] for r in runs) / len(runs) for i in range(3)
                )
                print(
                    f"{label} {n:>2} turns {pos:<6} acc {acc:6.1%}  fact gone {gone:6.1%}  loud {loud:6.1%}"
                )
                CACHE.write_text(json.dumps(cache))  # workers are idle, so this is safe
    print(
        f"{label}: log records at WARNING+ = {trap.count} | tokens used {sum(tokens_used):,}"
        f" | {time.perf_counter() - start:.0f}s"
    )


if __name__ == "__main__":
    sweep(ARMS[sys.argv[1]], sys.argv[1])
