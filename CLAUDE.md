# Ian Ho Deck Analyzer — Project Memory

## What This Project Is

An AI agent that mimics how Ian Ho (VP, Regional Cross Border at Shopee) reviews slide decks. When given a PDF deck, it generates:
1. A summary of the deck
2. Predicted questions Ian would ask (in his actual email style)
3. Suggested answers and likely follow-ups

**Goal:** Increase productivity by preparing teams for Ian's review before meetings.

## Architecture (Phase 1 — Claude Project)

The agent runs inside a **Claude Project** (claude.ai) with custom system prompt + uploaded knowledge files. No API access. No custom code running inside Claude — just prompt engineering and knowledge files.

**Files uploaded to Claude Project (in `Ian Email/` folder):**
- `system_prompt.md` — Core instructions. Paste into Claude Project custom instructions field. Contains two-pass workflow (extract data first, then generate questions) and "How Ian Reads a Slide" checklist.
- `persona_summary.md` — Ian's personality, communication style, analytical traits
- `worked_examples.md` — 3 complete deck-to-questions examples with **10 annotated trigger patterns** showing exact data → question reasoning chains
- `meeting_memory.md` — Ian's recurring concerns, open action items, "i remember" context by program (SIP, Swarm, KR/JP, CNLS, etc.)
- `domain_knowledge.md` — How SIP/Swarm/SCS/logistics models work, cross-program comparisons

**Pre-processing script (optional but improves accuracy):**
- `anomaly_extract.py` — Python script using pdfplumber. Extracts slide data from PDF, detects anomalies (RR misses, P&L issues, stated causes, market launches, assortment slides, cross-slide contradictions), cross-references meeting_memory.md, outputs `anomaly_brief.md`.
- Usage: `cd "Ian Email" && source .venv/bin/activate && python anomaly_extract.py "path/to/deck.pdf"`
- Output: `anomaly_brief.md` in same folder as PDF — upload alongside PDF to Claude Project

## Training Data

- `Ian Email/training_data/` — 33 threads from 2026, each with a PDF deck + `metadata.json` (email Q&A with Ian's verbatim questions)
- `Ian Email/training_data_2025/` — Historical 2025 threads
- Ian Ho is the questioner. Shuning Wang is Nicholas's boss.

## Current Accuracy (as of Apr 2026)

| Deck | Before Fixes | After Fixes A+B+C |
|---|---|---|
| SIP Weekly (thread-030) | 26.5% | 50.0% |
| SIP Monthly (thread-023) | 20.0% | 45.8% |

Scoring method: Compare predicted questions against Ian's verbatim questions from metadata.json. Full match = 1.0, partial = 0.5, miss = 0.0. Score = total / number of actual questions.

## The 3 Fixes (implemented)

**Fix A — Annotated Trigger Patterns:** `worked_examples.md` rewritten with 10 generalizable patterns (zero/gap in table, worst P&L row, cross-slide mismatch, stated cause, stuck rows, other market, crisis drill, aggregate metric, new proposal, memory match). Each question annotated with DATA → PATTERN → CHAIN.

**Fix B — Two-Pass Prompting:** `system_prompt.md` now instructs Claude to: (1) extract all table data and flag anomalies slide-by-slide BEFORE generating questions, (2) apply "How Ian Reads a Slide" checklist (highlight text first → worst row → zeros → stated cause → cross-slide memory → cross-program comparison).

**Fix C — Pre-Processing Script:** `anomaly_extract.py` detects: RR misses (<90%), MoM declines (>5%), P&L misses, masked losses, stated causes from highlight text, market launches, assortment/category slides, UE/pricing slides, multiple tables, delayed items, new proposals, compensation, crisis slides, acquisition tables. Scores and ranks slides by severity. Cross-references meeting_memory.md keywords.

## Known Remaining Gaps

1. **Deep data questions** — Ian asks for specific UE breakdowns, cell-level values ("show me how we price for incu SKUs"). The model can identify the slide but not generate the precise data question.
2. **Prior context numbers** — When Ian remembers a specific number from a past meeting and the current slide shows a different one, the model sometimes misses this.
3. **Slide selection for category/assortment slides** — Improved but not perfect. Ian questions these even when they look "clean" because he has strategic concerns.
4. **Cross-slide reconciliation** — Ian catches when two tables don't match. The script flags this but Claude doesn't always act on it.

## Key Technical Details

- Python venv at `Ian Email/.venv` (pdfplumber installed)
- `qa_examples.md` is legacy — content merged into `worked_examples.md`
- meeting_memory.md was auto-generated from all metadata.json files across threads
- The anomaly_extract.py MARKET LAUNCH, STATED CAUSE, ASSORTMENT/CATEGORY, UE/PRICING, and MULTIPLE TABLES detectors were added in the latest iteration

## Phase 2 Vision (not yet built)

A web app where:
1. User logs in via Google → agent auto-pulls emails with PDF attachments
2. Lists meetings for the day
3. User clicks a meeting → sees summary + predicted questions
4. Questions are editable; Ian's edits trigger a feedback loop to improve the model
5. `anomaly_extract.py` becomes the automated backend

## How to Continue Work

1. To improve accuracy: test more decks, score against metadata.json, identify failure patterns, update worked_examples.md or anomaly_extract.py
2. To update memory: edit `meeting_memory.md` with new recurring concerns from recent threads
3. To add new patterns: add to the 10-pattern table in `worked_examples.md` and corresponding detection in `anomaly_extract.py`
4. To test: run `python anomaly_extract.py "path/to/deck.pdf"`, upload PDF + anomaly_brief.md to Claude Project, compare output against metadata.json
