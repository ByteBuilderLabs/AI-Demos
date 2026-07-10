from agent import run
from crew import build_crew

TASK = ("Read .\\docs\\brief.md and .\\docs\\notes.md, combine them into one "
        "report at .\\out\\report.md, then call verify and fix what it flags.")

single_tokens = run(TASK)

crew = build_crew()
crew.kickoff()
crew_tokens = crew.usage_metrics.total_tokens

print(f"single agent   : {single_tokens:,} tokens")
print(f"four-agent crew: {crew_tokens:,} tokens")
print(f"crew / single  : {crew_tokens / single_tokens:.1f}x")