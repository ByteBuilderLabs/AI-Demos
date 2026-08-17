ERROR_MARKERS = (
    "error",
    "unavailable",
    "could not",
    "couldn't",
    "unable to",
    "no price",
    "failed",
)


def classify(answer: str, expected_price: str, crashed: bool) -> str:
    if crashed:
        return "visible_error"
    if expected_price in answer:
        return "recovered"
    if any(m in answer.lower() for m in ERROR_MARKERS):
        return "visible_error"
    return "silent_wrong"
