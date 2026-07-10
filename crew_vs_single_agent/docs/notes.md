# Working notes — Nimbus (raw, not cleaned up)

standup dump + open questions, don't treat as final

## Risks / things that could bite us
- Full reindex of the catalog (~4M docs) is the scary one. Last full
  reindex took 9 hours and locked writes. Need a zero-downtime plan or
  we eat an outage.
- Embedding cost: at 4M docs plus daily deltas, the bill could blow the
  quarter's infra budget. Nobody has priced this yet.
- p95 latency. Vector search adds a hop. If we can't hold p95 under
  300ms, the whole thing gets reverted.
- Staffing: Priya is out the first week of April. If reindex slips into
  that week, we lose the only person who knows the ingest pipeline.

## Open questions
- Which embedding model? Small and cheap vs the big one, undecided.
- Blend scores in the app layer or push into ES rank_feature?
- Fallback if the vector index is down mid-query. Degrade to
  keyword-only? Probably yes.

## Random
- Marco wants a demo before the 10% rollout
- old spike branch is `spike/hybrid-search`, mostly throwaway
- QA needs a full week, so realistic freeze is more like April 22