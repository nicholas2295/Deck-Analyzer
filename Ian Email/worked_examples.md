# Worked Examples — How Ian Ho Reviews Decks

These are 3 complete examples showing exactly how Ian selects slides to question, what he asks, and what he skips.

**NEW: Each question is annotated with the DATA on the slide that triggered it, the PATTERN that made Ian stop, and the CHAIN of reasoning from data to question. Learn these patterns — they apply to ANY deck, not just these specific slides.**

---

## Example 1: KR/JP Bi-weekly Update (thread-024, 20 Mar 2026)

**Deck:** KR/JP Bi-weekly Update_260320 (~40 slides)
**Slides Ian questioned:** 11, 12, 16, 19, 21-22, 31, 36 (7 slides)
**Total questions:** 17
**Slides Ian skipped:** P&L overview, OKR summary, previous meeting tracker, appendix, slides that were on track

### Ian's verbatim questions with trigger annotations:

```
thanks

slide 11
- how is our ado in BR so far?
- have we considered FBS for BR yet?
```
**PATTERN: [Market with low presence in a multi-market table]**
DATA: LFF-by-market table shows BR as a small market with ~7% contribution to KR. Most slides focus on bigger markets (VN, TH, MY). BR appears as a row but with minimal data.
CHAIN: Ian scans the table → finds a market that seems under-discussed → asks an open "how is X?" to surface whether it's being neglected.
FOLLOW-UP PATTERN: After asking about performance, he immediately asks about the NEXT lever: "have we considered FBS?" — this is his standard "performance → next step" cascade.

```
slide 12
- for VN, we are still unable to use local FBS?
- still have to utilize LFF?
```
**PATTERN: [Zero or gap in a capability column]**
DATA: LFF detail table shows VN has no local FBS capability. System dev for KRSC-to-VN local FBS is "in progress, ETA Q2-Q3."
CHAIN: Ian scans the table → VN column shows a gap (no FBS) → asks about that specific market. He does NOT ask about markets that have FBS. He asks about the one that DOESN'T.
NOTE: When you see a zero/blank/gap in a table, always ask about THAT cell. Never ask about the cells that are fine.

```
slide 16
- for #2 >> what is the issue around API integration right now?
- for #9 >> how are they doing right now?
```
**PATTERN: [Seller/brand acquisition table with pending/slow rows]**
DATA: Seller acquisition table with numbered rows. #2 (Musinsa) shows "waiting for system requirements/specs" — stuck in API integration. #9 shows "2 brands confirmed (of 100+)" — just started, marketing not begun.
CHAIN: Ian scans the table → finds rows that are stuck or very early stage → references them by number ("for #2 >>") and asks short questions about the blocker.
NOTE: Ian always references ROW NUMBERS in acquisition tables. He picks 2-3 rows that look stuck or interesting, not every row.

```
slide 19
- how does the situation in JP look like?
- given that we will have alot of new hires, should we relook our onboarding process as well?
```
**PATTERN: [Ask about the OTHER market/region first]**
DATA: Slide 19 shows KR RM capability data. JP is not the focus of this slide.
CHAIN: Ian sees KR data → immediately asks about JP (the market NOT shown) → then asks a practical follow-up about onboarding process for new hires.
NOTE: When a slide shows data for one market, Ian's FIRST question is always about the OTHER market: "how does JP look?" on a KR slide, "how is KR doing?" on a JP slide.

```
slide 21 - 22
- what is the vendor working on from now till mid Apr to be able to improve BWT?
- Do we know what the key issue is right now, and what exactly is the vendor trying to fix?
- and do we know why it will take another month to fix it?
- i remember we were looking at getting another CC vendor, where did we land on that?
- did we proactively increase the EDT so that we do not disappoint on buyer experience?
```
**PATTERN: [Ongoing crisis — deep drill with 5+ questions]**
DATA: BWT still elevated. Order-to-delivery taking 12+ days. Sagawa vendor issues. Limited tracking (no line haul integration). New vendor RFQ sent to 12 vendors on 3/20, decision by Apr 24, go-live Jul 1. EDT increased by +10 days from Feb 11.
CHAIN: Ian sees a crisis slide → drills DEEP with a predictable 5-question chain: (1) what is vendor doing? (2) what is the root cause? (3) why so long to fix? (4) prior context on alternative vendor (5) mitigation check (did we adjust EDT?).
NOTE: This 5-question chain is Ian's STANDARD pattern for any crisis/delay slide. Apply it whenever you see a logistics issue, vendor problem, or system outage.

```
slide 31
- have we paid out the SLS + compensation yet?
- where did we land on getting compensation from vendor?
```
**PATTERN: [Compensation/payout — always starts with simple yes/no]**
DATA: Seller compensation first round expected Apr W1 (as announced to sellers). Vendor compensation claim being scoped with legal, aligned to submit later Q2 to maintain relationship with Sagawa.
CHAIN: Ian's FIRST question is always the simple yes/no: "have we paid yet?" — not about process, not about who gets what. Just: did the money go out? THEN he asks about getting compensated by the vendor.
NOTE: On ANY compensation slide, always generate: (1) "have we paid out yet?" then (2) "where did we land on getting compensation from [vendor]?"

```
slide 36
- i thought we started to onboard F&B SKUs, how is the performance so far?
- I remember we wanted to push F&B harder, but does not seem like much impact?
```
**PATTERN: [Weak category + prior context "i thought" / "i remember"]**
DATA: F&B performance table shows ADO went from 2.3 (Jan) to 17.0 (Mar) — growth exists but absolute numbers are small. Only 1 new F&B brand by H1. 11 managed shops out of 343 whitelist shops.
CHAIN: Ian remembers pushing for F&B in prior meetings → sees current data → acknowledges some progress but frames it as insufficient: "does not seem like much impact?"
NOTE: Ian uses "i thought" when he remembers a COMMITMENT and "i remember" when he recalls a DISCUSSION. Both are prior-context triggers. Always include 2-3 of these per deck, sourced from meeting_memory.md.

### What he skipped and why:
P&L overview (KR on track, JP over-delivering), previous meeting tracker, OKR backup table, marketing performance slides (no obvious issue), Counter CP slides (nothing alarming), appendix.

---

## Example 2: SIP Weekly Update (thread-012, week ending 30 Jan 2026)

**Deck:** SIP weekly update_week ending 30 Jan (~28 slides SIP + ~5 slides Swarm)
**Slides Ian questioned:** SIP: 3, 4, 7, 8, 13, 15, 20, 23, 27
**Total questions:** 18

### Ian's verbatim questions with trigger annotations:

```
Slide 3
- Why is seller standalone for CNSIP negative?
- Swarm is going to lose much more than expected?
```
**PATTERN: [P&L table — find the worst rows]**
DATA: P&L table shows CNSIP seller standalone at breakeven ($8k-$67k range) but below target (+$122k) due to one-time 2% commission rebate system issue. Swarm is missing target badly.
CHAIN: Ian scans the P&L table → finds CNSIP standalone is below target and Swarm is the worst performer → asks about each separately. He does NOT cite the numbers. He says "negative?" and "lose much more than expected?"
NOTE: On P&L slides, find the 1-2 rows with the worst RR% or biggest miss vs target. Those are the rows Ian questions.

```
Slide 4
- Without Flash, we still have SPX?
```
**PATTERN: [Logistics change — operational continuity check]**
DATA: Flash has been discontinued. SPX is the primary last-mile provider. ~200 orders in East Malaysia not yet serviceable by SPX.
CHAIN: Ian sees a logistics provider change → asks the simple yes/no: do we still have coverage?
NOTE: When a vendor/partner is removed, Ian always asks: "do we still have [alternative]?" — a one-line operational continuity check.

```
Slide 7
- P&L different than Slide 3?
- Why P&L drop so much MOM?
- Seller P&L should be positive for CNSIP regardless of target setting?
```
**PATTERN: [Cross-slide contradiction — comparing two P&L slides]**
DATA: Slide 7 shows another P&L view. Slide 3 showed the first P&L view. The numbers are actually consistent (both show breakeven, -$122k vs target, -$94k MoM), but Ian didn't see that immediately.
CHAIN: Ian held Slide 3's numbers in memory → reached Slide 7 → noticed what looked like a different number → asked "P&L different than Slide 3?" → then drilled into MoM and whether CNSIP should be positive regardless.
NOTE: THIS IS THE MOST IMPORTANT PATTERN. Whenever you see two P&L slides, COMPARE their numbers. If they look different (or even ambiguous), ask: "P&L different than Slide [earlier slide]?"

```
Slide 8
- I thought Swarm UE was expected to be -2.X?
- Why is it -1 here?
```
**PATTERN: [Prior context — remembered number contradicts current slide]**
DATA: Swarm UE shown as approximately -$1.00 on the slide. Ian remembered from a prior meeting that it was expected to be -$2.X.
CHAIN: Ian remembers a specific number from before → sees a different number on the slide → challenges the discrepancy.
NOTE: Check meeting_memory.md for any specific numbers Ian has remembered. If the slide shows a different value, generate an "I thought" question.

```
Slide 13
- What are next steps for #6?
- When is it ready?
- When will we pass chat to sellers?
- When will we be able to use seller vouchers from export market?
```
**PATTERN: [Product roadmap — spot slow/TBC items + cascade into recurring asks]**
DATA: Product roadmap table. #6 (KRSIP system) is in PRD phase, ETA end Mar'26 but delayed. Chat to sellers: PM feasibility, ETA end Jun. Seller vouchers: biz requirement done, HQ legal pending, ETA end-Q2.
CHAIN: Ian scans the roadmap → finds #6 is slow → asks about it by number → then cascades into his recurring product concerns (chat to sellers, seller vouchers) which appear as other items on the same table.
NOTE: On roadmap slides, Ian asks about 1-2 slow items by number ("for #6 >>"), then always asks about his recurring product concerns (chat passback, seller vouchers) regardless of their status.

```
Slide 15
- For direct selling to BN, do sellers who are already operating for MY need to agree again?
```
**PATTERN: [New market expansion — operating model mechanics question]**
DATA: BN expansion slide showing opt-out model for existing MY sellers.
CHAIN: Ian sees a new market being opened → asks the practical operating model question: do sellers need to do anything?
NOTE: When you see market expansion, check domain_knowledge.md for how the operating model works. Ian always asks the "how does this work for the seller?" question.

```
Slide 20
- Is there a view to show ADO by export lanes?
- Does it make sense to work with local ERPs in ID/MY/VN to help sellers export?
- Similar to how we work with JST in CN?
```
**PATTERN: [Data view request + cross-program comparison]**
DATA: Slide shows Direct vs SIP scale data. Direct ADO = 17% of SIP. Lane-level breakdown available.
CHAIN: Ian wants to see the data cut differently ("by export lanes") → then generates a strategic idea ("work with local ERPs?") → then makes a cross-program comparison ("similar to JST in CN?").
NOTE: Ian's cross-program comparisons always follow domain_knowledge.md patterns. Check the "Cross-Program Comparisons" table — if the current topic matches a row, generate the comparison question.

```
Slide 23
- Think most markets have BSC as well on top of SG
```
**PATTERN: [Observation about a table — correcting an apparent gap]**
DATA: BSC coverage table showing which lanes have BSC by market. SG is highlighted, but other markets also have it.
CHAIN: Ian reads the table → notices the framing seems to focus on SG → points out that other markets also have BSC.
NOTE: When a slide focuses on one market but the data shows others are similar, Ian makes a short corrective observation.

```
Slide 27
- SIP is not in VN right now?
- Do we know why?
```
**PATTERN: [Market absence — simple discovery question]**
DATA: VN had SIP but it was closed H2 2022 due to low ADO (~600) and high costs. Re-entry planned starting TH→VN in Mar 2026.
CHAIN: Ian spots that VN is absent from the SIP coverage → asks the simple question → follows up with "do we know why?"
NOTE: When a market is MISSING from a program coverage slide, always ask about it.

---

## Example 3: SIP Monthly Meeting (thread-018, Feb 2026)

**Deck:** SIP Monthly Meeting 20260226 pre-reads (~55 slides)
**Slides Ian questioned:** 11, 14, 27, 37, 51, 52 (6 slides)
**Total questions:** 9

### Ian's verbatim questions with trigger annotations:

```
Slide 11
- It is not quite clear what #1 is about or why it is really needed. In general, seller vouchers are set for all buyers?
```
**PATTERN: [Confusing content — "not clear" / "do not understand"]**
DATA: Slide shows SIP seller voucher sync legal requirements. #1 is "Voucher eligibility based on end-buyer profile" — revamp shop vouchers to merchant vouchers, sync buyer profile eligibility rules, sync voucher quotas. Marked as "High" effort with note "Fundamental change to voucher mechanism."
CHAIN: Ian reads the description → finds it unclear WHY #1 is needed → says so directly: "not quite clear what #1 is about." Then asks a clarifying question about the underlying assumption.
NOTE: When a slide is confusing, Ian says so bluntly. Generate a "not quite clear" or "I do not understand" question when the slide content is dense or the rationale isn't obvious.

```
Slide 14
- Ok
```
**PATTERN: [No concerns — "Ok" acknowledgment]**
DATA: PH co-investment proposal with Table 1 showing FY26 options. SIP counter-proposal: 3-month trial, combined P&L +4.3% vs base. Clear framing with approval line.
CHAIN: Ian reads it → the proposal is well-structured and makes sense → acknowledges with "Ok."
NOTE: "Ok" means Ian read the slide and has no questions. When a slide is clear, well-structured, and the recommendation makes sense, Ian might not question it at all. Do not force questions on good slides.

```
Slide 27
- When will we transfer chat directly to seller?
```
**PATTERN: [Recurring product ask — meeting_memory.md topic on a related slide]**
DATA: CS bot buyer journey slide showing FAQ → chatbot → agent flow. No ETA for direct-to-seller chat on this slide.
CHAIN: Ian sees a CS/chat-related slide → this triggers his recurring concern about passing chat directly to sellers (from meeting_memory.md) → asks the timeline question even though the slide doesn't address it.
NOTE: When a slide's TOPIC matches a concern in meeting_memory.md, Ian asks about the memory item even if the slide doesn't cover it.

```
Slide 37
- Can we split up TR here further?
- Into mandatory comms, optional comms, transaction fees and paid ads?
- And compare it with local MP?
- The TR seems low in general, and I do not think it is purely because of paid ads
```
**PATTERN: [Aggregate metric — wants the breakdown + local comparison]**
DATA: Direct selling P&L slide showing MP Takerate% = 8.9% total. Breakdown by import market (SG 10.2%, MY 8.6%, TH 8.4%, PH 6.7%). But NO split into components (mandatory comms vs optional comms vs transaction fees vs paid ads).
CHAIN: Ian sees an aggregate TR% → immediately wants the component breakdown ("split up further") → wants to compare against local MP benchmarks → then makes a judgment: "seems low, not purely because of paid ads."
NOTE: When you see an aggregate metric (total TR%, total P&L) without a component breakdown, Ian ALWAYS asks for the breakdown. Check domain_knowledge.md for what components he expects (mandatory comms, optional comms, transaction fees, paid ads).

```
Slide 51
- Not quite sure how this will work in general
- Which markets have compulsory AGP for now?
- When do we foresee launching AGP for direct sellers?
```
**PATTERN: [New proposal — standard 3-question sequence]**
DATA: Direct ads program proposal — 5% seller escrow for ads in exchange for 5% platform PRM rebate. Pilot for managed mature sellers in Mar. Mandatory AGP by market listed on a different slide (49).
CHAIN: Ian sees a new proposal → follows his standard sequence: (1) "how does this work?" / "not quite sure" → (2) asks about current state ("which markets?") → (3) asks about timeline ("when for direct sellers?").
NOTE: For ANY new initiative or "For Discussion" item, generate Ian's standard 3-step sequence: (1) how does it work / confusion, (2) current state question, (3) timeline question. Check domain_knowledge.md for cross-program comparisons.

```
Slide 52
- How does it compare with shops in the local market
- I remember we wanted to port their seller vouchers in import market over to export market?
- How is that fix coming along?
```
**PATTERN: [Performance table + cross-program comparison + prior context]**
DATA: Direct vs CNCB seller voucher metrics. SG SV ADO coverage 72.5% Direct vs 43.0% CNCB. MY much lower at 11.7% vs 45.8%. Resync feature in dev pipeline, ETA end-Apr.
CHAIN: Ian sees Direct vs CNCB comparison → immediately asks how it compares to LOCAL market (a third benchmark not shown) → then triggers his recurring concern about seller voucher porting → asks about progress.
NOTE: When a slide compares two programs, Ian often asks about a THIRD benchmark (usually local MP). Then he layers on a meeting_memory.md "i remember" question about a related topic.

### What he skipped and why:
Most of the 55-slide deck. P&L topline (on track), Swarm performance (covered in weekly), direct selling metrics (no red flags), market-by-market operational updates, marketing slides, appendix. Monthly decks = fewer slides questioned, deeper per slide.

---

## Summary: The 10 Trigger Patterns

| # | Pattern | Ian's reaction | Example question |
|---|---------|---------------|-----------------|
| 1 | Zero/blank/gap in table | Ask about THAT cell specifically | "for VN, we are still unable to use local FBS?" |
| 2 | Worst row in P&L table | Ask about THAT program | "why is seller standalone for CNSIP negative?" |
| 3 | Cross-slide number mismatch | Challenge the contradiction | "P&L different than Slide 3?" |
| 4 | Stated cause in highlight text | Question WHETHER the cause is correct | "we would need to adjust if it is indeed to PH spending more?" |
| 5 | Stuck/pending rows in tables | Reference by row number | "for #2 >> what is the issue?" |
| 6 | Other market not shown | Ask about it first | "how does the situation in JP look like?" |
| 7 | Crisis/delay slide | 5-question deep drill chain | "what is the vendor working on?" → root cause → timeline → alternative → mitigation |
| 8 | Aggregate metric, no breakdown | Ask for the split | "can we split up TR further?" |
| 9 | New proposal | 3-question sequence | "how does this work?" → "which markets?" → "when?" |
| 10 | meeting_memory.md topic match | "i remember" / "i thought" | "i remember we wanted to push F&B harder" |
