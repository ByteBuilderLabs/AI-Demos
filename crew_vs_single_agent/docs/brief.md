# Project Brief: Nimbus Search Migration

## Overview
Replace the keyword-only search on the customer dashboard with hybrid
search (keyword + vector). Users complain results miss obvious matches
when they paraphrase. The goal is better recall on natural-language
queries without hurting p95 latency.

## Scope
- Stand up a vector index alongside the existing Elasticsearch cluster
- Add an embedding step to the ingest pipeline
- Blend keyword and vector scores behind a single `/search` endpoint
- Ship behind a feature flag, roll out to 10% of traffic first

Out of scope: redesigning the search UI, changing ranking for the
internal admin tools.

## Ownership
Tech lead: Priya Nair (Search Platform team). Product partner: Marco Reyes.

## Timeline
Target GA: April 30. Feature-flag rollout to 10% by April 9.
Code freeze April 25.