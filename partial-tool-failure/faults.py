from tools import lookup_account, get_discount, calculate

TOOLS = {f.__name__: f for f in (lookup_account, get_discount, calculate)}
ORDER = list(TOOLS)


def inject(run, soft=False):
    broken = ORDER[run % len(ORDER)]

    def fail(**kwargs):
        if soft:
            return {}
        raise TimeoutError(f"{broken} timed out")

    return {**TOOLS, broken: fail}, broken
