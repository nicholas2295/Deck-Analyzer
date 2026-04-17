#!/usr/bin/env python3
"""
Pre-processing script for Ian Ho Deck Analyzer.
Extracts slide data from a PDF, detects anomalies, cross-references
meeting_memory.md, and outputs a structured anomaly_brief.md.

Usage:
    source .venv/bin/activate
    python anomaly_extract.py <path_to_deck.pdf>

Output: anomaly_brief.md in the same directory as the PDF.
"""

import sys
import re
import os
import pdfplumber


MEMORY_KEYWORDS = {
    "SIP": {
        "seller pricing": "Ian's #1 concern: 'how can we structurally go to sellers to reduce price?'",
        "seller voucher": "Ian tracks seller voucher porting — 'i remember we wanted to port seller vouchers'",
        "direct selling": "Ian tracks direct growth pace — 'direct does not feel like it is growing'",
        "assortment": "Ian tracks assortment optimization — 'i remember relook how we select, price, rebate for unique assortment'",
        "unique": "Ian tracks unique assortment strategy — 'are we selecting the right assortment to list and push?'",
        "chat": "Ian tracks chat passback to sellers — 'when will we pass chat to sellers?'",
        "charge seller": "Ian wants to start charging sellers for services",
        "furniture": "Ian asks 'are we not pushing for furniture?' on category slides",
        "category": "Ian questions category strategy — 'are we pushing for the right categories?'",
        "incubat": "Ian asks for UE breakdown of incubation SKUs — 'why do we need to lose $X per order?'",
        "black stock": "Ian asks 'how are we accounting for the p&l of black stock?'",
        "blackstock": "Ian asks 'how are we accounting for the p&l of black stock?'",
    },
    "Swarm": {
        "target": "Ian always asks 'do we have targets?' for Swarm",
        "lead": "Ian challenges 'what does leads mean?' — wants onboarding numbers",
        "ue": "Ian remembers specific UE targets — 'i thought Swarm UE was -2.X'",
        "jst": "Ian tracks JST seller growth",
        "wdt": "Ian tracks WDT seller growth",
    },
    "KR/JP": {
        "commission": "Ian tracks commission/TR increase timing for KR/JP",
        "take rate": "Ian tracks commission/TR increase timing for KR/JP",
        "lff": "Ian pushes LFF penetration — 'if VN can > 50%, why not other markets?'",
        "fbs": "Ian tracks FBS availability for CB sellers — 'FBS tag on SKU'",
        "f&b": "Ian pushes F&B harder — 'i remember we wanted to push F&B'",
        "bwt": "Ian drills deep on BWT/logistics crises",
        "compensation": "Ian always asks 'have we paid out compensation yet?'",
        "vendor": "Ian tracks CC vendor alternatives",
    },
    "CNLS": {
        "fbs": "Ian tracks FBS penetration vs TT — 'where do we stand vs TT?'",
        "3pf": "Ian compares 3PF vs FBS penetration by market",
        "fbs tag": "Ian asks 'where did we land on FBS tag on SKU?'",
    },
    "General": {
        "fsc": "Ian asks about FSC budgeting and oil price assumptions",
        "fuel surcharge": "Ian asks about FSC budgeting and oil price assumptions",
        "import tax": "Ian questions option selection and alignment",
        "scs": "Ian compares SIP LFF to SCS LFF model",
        "lovito": "Ian is most concerned about Lovito growth/breakeven",
        "npc": "Ian tracks NPC / price competitiveness",
    },
}


def extract_slides(pdf_path):
    """Extract text from PDF. Each PDF page = one slide."""
    slides = {}

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text() or ""
            slide_num = i + 1
            num_match = re.search(r"(?:^|\n)\s*(\d{1,3})\s*$", page_text)
            if num_match:
                detected = int(num_match.group(1))
                if 1 <= detected <= len(pdf.pages) + 5:
                    slide_num = detected
            slides[slide_num] = page_text

    return slides


def parse_rr_values(text):
    """Find all RR% values in text."""
    matches = re.findall(r"(\d+)%\s*(?:RR|rr)", text)
    return [(int(m)) for m in matches]


def detect_anomalies(slide_num, text):
    """Detect anomalies in a single slide's text."""
    anomalies = []
    text_lower = text.lower()

    rr_pattern = re.findall(r"([A-Za-z][A-Za-z/]{1,20})\s+[\d,.]+\s+[\d,.]+\s+(\d{2,3})%", text)
    for name, rr_str in rr_pattern:
        rr = int(rr_str)
        if 1 <= rr < 90:
            severity = "SEVERE" if rr < 50 else "MODERATE" if rr < 80 else "MILD"
            anomalies.append(f"MISS ({severity}): '{name}' at {rr}% RR")

    rr_standalone = re.findall(r"(\d{2,3})%\s*RR\b", text)
    for rr_str in rr_standalone:
        rr = int(rr_str)
        if 1 <= rr < 90 and not any(f"{rr}%" in a for a in anomalies):
            severity = "SEVERE" if rr < 50 else "MODERATE" if rr < 80 else "MILD"
            anomalies.append(f"MISS ({severity}): {rr}% RR detected on slide")

    mom_pattern = re.findall(r"(-\d+)%\s*(?:MoM|mom|MOM)", text)
    for mom_str in mom_pattern:
        mom = int(mom_str)
        if mom <= -5:
            anomalies.append(f"DECLINE: {mom}% MoM decline")

    neg_dollar = re.findall(r"-\$[\d,.]+k?\s", text)
    for val in neg_dollar[:3]:
        val_clean = val.strip()
        if "target" in text_lower or "vs target" in text_lower:
            anomalies.append(f"P&L MISS: {val_clean} appears in P&L context")

    if re.search(r"(?:standalone|seller).*(?:negative|loss|-\$)", text_lower):
        if re.search(r"(?:total|combined|mp pc2).*(?:positive|\+\$|above target)", text_lower):
            anomalies.append("MASKED LOSS: Standalone P&L negative but total P&L positive — Ian asks 'is this sustainable?'")

    zero_patterns = re.findall(r"(\w{2,})\s+(?:0|0%|0\.0%|nil|-)\s", text)
    for market in zero_patterns[:3]:
        if market.upper() in ("VN", "SG", "MY", "TH", "PH", "ID", "TW", "BR", "KR", "JP", "BN"):
            anomalies.append(f"GAP: {market.upper()} shows zero/blank — Ian asks about this market specifically")

    delayed_patterns = re.findall(r"(?:#\d+|item\s+\d+)[^\n]*(?:TBC|Pending|Delayed|delayed|pending|tbc|In Progress)", text)
    for item in delayed_patterns[:5]:
        item_clean = item.strip()[:80]
        anomalies.append(f"DELAYED: '{item_clean}'")

    if re.search(r"(?:tbc|pending|delayed)", text_lower) and not delayed_patterns:
        tbc_count = len(re.findall(r"(?:TBC|Pending|Delayed)", text, re.IGNORECASE))
        if tbc_count >= 2:
            anomalies.append(f"DELAYED: {tbc_count} items marked TBC/Pending/Delayed on this slide")

    if re.search(r"(?:for discussion|new initiative|proposal|pilot|new program)", text_lower):
        anomalies.append("NEW PROPOSAL: This slide contains a new initiative or 'For Discussion' item — Ian uses his 3-question sequence")

    if re.search(r"(?:compensation|payout|paid out|reimburse)", text_lower):
        anomalies.append("COMPENSATION: Ian always asks 'have we paid out yet?' first")

    if re.search(r"(?:bwt|buyer wait|delivery delay|logistics.*delay|vendor.*issue|cc.*delay)", text_lower):
        anomalies.append("CRISIS: Logistics/delay slide — Ian uses 5-question deep drill chain")

    if re.search(r"(?:acquisition|onboard|seller.*table|brand.*table|pipeline)", text_lower):
        if re.search(r"#\d+", text):
            anomalies.append("ACQUISITION TABLE: Ian references specific row numbers — 'for #N >>'")

    # STATED CAUSE detection: extract causal phrases from highlights
    cause_patterns = re.findall(
        r"(?:mainly due to|driven by|caused by|impacted by|due to|because of)\s+(.{15,120})",
        text, re.IGNORECASE,
    )
    for cause in cause_patterns[:3]:
        cause_clean = cause.split(".")[0].strip()[:100]
        anomalies.append(
            f"STATED CAUSE: '{cause_clean}' — Ian questions WHETHER this cause is correct or if targets should change"
        )

    # MARKET LAUNCH detection: new lane/market rollout slides
    if re.search(r"(?:launch|go.?live|rollout|re.?enter|expansion)", text_lower):
        if re.search(r"(?:lane|market|export|import|seller.*pitch|opt.?in|acceptance)", text_lower):
            anomalies.append(
                "MARKET LAUNCH: New market/lane launch — Ian asks operational questions: "
                "'what % of SKUs are live?', 'are we leaving anything on the table?', 'acceptance rate?'"
            )

    # ASSORTMENT / CATEGORY detection: slides about SKU selection, pricing strategy, category push
    if re.search(r"(?:assortment|sku.*select|category|furniture|fashion|unique.*sku|price.*competi|listing.*price|sku.*profile)", text_lower):
        anomalies.append(
            "ASSORTMENT/CATEGORY: Ian asks about category strategy — "
            "'are we pushing for [category]?', 'are we selecting the right assortment?'"
        )

    # UE BREAKDOWN detection: slides showing UE, CPO, or pricing mechanics
    if re.search(r"(?:ue breakdown|unit econom|cpo.*breakdown|pricing.*model|markup|incubat.*sku|mature.*sku)", text_lower):
        anomalies.append(
            "UE/PRICING: Slide shows UE or pricing — Ian asks 'show me the UE breakdown', "
            "'why do we need to lose $X per order?'"
        )

    # TABLE WITH MULTIPLE VIEWS detection: slides with >1 table or multiple scenarios
    table_markers = len(re.findall(r"(?:Table \d|Option \d|Scenario|Base Case|vs )", text))
    if table_markers >= 2:
        anomalies.append(
            "MULTIPLE TABLES: Slide has multiple tables/scenarios — "
            "Ian asks 'can you reconcile these?' or 'give me monthly and annual figures'"
        )

    return anomalies


def extract_highlight_text(text):
    """Extract bullet-point highlights from slide text."""
    highlights = []
    for line in text.split("\n"):
        line_stripped = line.strip()
        if line_stripped.startswith("●") or line_stripped.startswith("•") or line_stripped.startswith("-"):
            if len(line_stripped) > 20:
                highlights.append(line_stripped[:200])
        elif re.match(r"^Highlights?", line_stripped, re.IGNORECASE):
            highlights.append("[HIGHLIGHT SECTION]")
    return highlights


def check_memory_matches(text):
    """Cross-reference slide text against meeting_memory.md keywords.
    Only triggers if both the program context and specific keyword are present."""
    matches = []
    text_lower = text.lower()

    program_indicators = {
        "SIP": ["sip", "local sip", "cnsip", "seller voucher", "direct selling"],
        "Swarm": ["swarm", "jst", "wdt"],
        "KR/JP": ["kr", "jp", "krsip", "f&b", "bwt", "sagawa", "lff"],
        "CNLS": ["cnls", "cncb", "cn seller"],
        "General": [],
    }

    for category, keywords in MEMORY_KEYWORDS.items():
        indicators = program_indicators.get(category, [])
        if indicators and not any(ind in text_lower for ind in indicators):
            continue

        for keyword, memory_note in keywords.items():
            kw = keyword.lower()
            if kw in text_lower:
                if kw in ("target", "ue", "lead"):
                    program_words = program_indicators.get(category, [])
                    if not any(pw in text_lower for pw in program_words):
                        continue
                matches.append(f"MEMORY ({category}): {memory_note}")

    return list(set(matches))


def detect_cross_slide_issues(slides):
    """Detect cross-slide contradictions and patterns."""
    issues = []

    def detect_period(text):
        """Detect which time period a slide covers (e.g., 'Jan', 'Feb EOM', 'Mar MTD')."""
        text_lower = text.lower()
        months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
        found = []
        for m in months:
            if re.search(rf"\b{m}\b", text_lower):
                found.append(m)
        qualifier = ""
        if "eom" in text_lower or "end of month" in text_lower:
            qualifier = " EOM"
        elif "mtd" in text_lower or "month to date" in text_lower:
            qualifier = " MTD"
        elif "projection" in text_lower or "forecast" in text_lower:
            qualifier = " proj"
        if found:
            return found[-1] + qualifier
        return None

    pnl_slides = {}
    for num, text in slides.items():
        if re.search(r"(?:p&l|P&L|pnl|standalone|seller.*p.*l)", text, re.IGNORECASE):
            values = re.findall(r"-?\$[\d,.]+k?", text)
            if values:
                period = detect_period(text)
                pnl_slides[num] = {"values": values[:10], "period": period}

    pnl_nums = sorted(pnl_slides.keys())
    # Group by period — only compare slides with the SAME period (or unknown period)
    from collections import defaultdict
    period_groups = defaultdict(list)
    for num in pnl_nums:
        p = pnl_slides[num]["period"] or "unknown"
        period_groups[p].append(num)

    for period, group_nums in period_groups.items():
        if len(group_nums) >= 2:
            first = group_nums[0]
            first_vals = set(pnl_slides[first]["values"])
            for later in group_nums[1:]:
                later_vals = set(pnl_slides[later]["values"])
                only_first = first_vals - later_vals
                only_later = later_vals - first_vals
                if only_first and only_later:
                    period_label = f" (both cover {period})" if period != "unknown" else ""
                    issues.append(
                        f"CROSS-SLIDE MISMATCH: Slide {first} has {list(only_first)[:3]} "
                        f"but Slide {later} has {list(only_later)[:3]}{period_label} — "
                        f"Ian asks 'P&L different than Slide {first}?' and 'i cannot reconcile the 2 tables'"
                    )

    # If multiple periods exist, note for context
    if len(period_groups) >= 3:
        period_summary = ", ".join(f"{p}: slides {','.join(str(s) for s in nums)}" for p, nums in period_groups.items() if p != "unknown")
        if period_summary:
            issues.append(f"CROSS-SLIDE NOTE: P&L slides cover different periods ({period_summary}) — compare WITHIN same period only")

    # FSC / cost slides with multiple tables
    fsc_slides = [n for n in slides if re.search(r"(?:fsc|fuel surcharge|oil price|cost.*impact)", slides[n].lower())]
    if len(fsc_slides) >= 2:
        issues.append(
            f"CROSS-SLIDE FSC: Slides {', '.join(str(s) for s in fsc_slides)} both cover FSC/cost — "
            f"Ian asks 'can you reconcile?' and 'what oil prices are we modelling?'"
        )

    swarm_slides = [n for n in slides if re.search(r"(?:^|\n)\s*swarm", slides[n], re.IGNORECASE | re.MULTILINE)]
    if swarm_slides:
        issues.append(
            f"SWARM SECTION: Slides {', '.join(str(s) for s in swarm_slides)} — "
            f"Ian questions Swarm SEPARATELY. Check for: targets, leads vs onboarding, UE, and comparison vs prior month."
        )

    return issues


def get_slide_title(text):
    """Extract a likely title from slide text."""
    lines = [l.strip() for l in text.split("\n") if l.strip() and not l.strip().startswith("Private")]
    for line in lines[:3]:
        if len(line) > 10 and not re.match(r"^\d+$", line):
            return line[:120]
    return "(no title detected)"


def score_slide(anomalies, memory):
    """Score a slide by severity for ranking. Higher = more likely Ian questions it."""
    score = 0
    for a in anomalies:
        if "SEVERE" in a:
            score += 10
        elif "MODERATE" in a:
            score += 6
        elif "MILD" in a:
            score += 3
        elif "MASKED LOSS" in a:
            score += 8
        elif "CRISIS" in a:
            score += 9
        elif "CROSS-SLIDE MISMATCH" in a:
            score += 8
        elif "NEW PROPOSAL" in a:
            score += 7
        elif "COMPENSATION" in a:
            score += 7
        elif "STATED CAUSE" in a:
            score += 7
        elif "MARKET LAUNCH" in a:
            score += 6
        elif "ASSORTMENT" in a:
            score += 6
        elif "UE/PRICING" in a:
            score += 6
        elif "MULTIPLE TABLES" in a:
            score += 6
        elif "ACQUISITION TABLE" in a:
            score += 5
        elif "DECLINE" in a:
            score += 5
        elif "P&L MISS" in a:
            score += 6
        elif "GAP" in a:
            score += 6
        elif "DELAYED" in a:
            score += 3
    for _ in memory:
        score += 2
    return score


def generate_brief(pdf_path, slides):
    """Generate the anomaly brief markdown."""
    output = []
    output.append(f"# Anomaly Brief — {os.path.basename(pdf_path)}")
    output.append(f"\nGenerated by anomaly_extract.py. Upload this alongside the PDF to Claude Project.\n")
    output.append(f"**Total slides:** {len(slides)}\n")

    cross_issues = detect_cross_slide_issues(slides)
    if cross_issues:
        output.append("## Cross-Slide Alerts\n")
        for issue in cross_issues:
            output.append(f"- {issue}")
        output.append("")

    slide_data = {}
    for num in sorted(slides.keys()):
        text = slides[num]
        title = get_slide_title(text)
        anomalies = detect_anomalies(num, text)
        highlights = extract_highlight_text(text)
        memory = check_memory_matches(text)
        severity = score_slide(anomalies, memory)
        slide_data[num] = {
            "title": title, "anomalies": anomalies,
            "highlights": highlights, "memory": memory, "score": severity,
        }

    ranked = sorted(
        [(num, d) for num, d in slide_data.items() if d["anomalies"] or d["memory"]],
        key=lambda x: x[1]["score"],
        reverse=True,
    )
    clean_slides = [num for num in sorted(slides.keys()) if not slide_data[num]["anomalies"] and not slide_data[num]["memory"]]

    top_n = min(8, len(ranked))
    top_slides = ranked[:top_n]
    lower_slides = ranked[top_n:]

    output.append(f"## TOP {top_n} PRIORITY SLIDES (question these)\n")
    for num, d in top_slides:
        output.append(f"### Slide {num} — {d['title']} (severity: {d['score']})\n")

        if d["highlights"]:
            output.append("**Highlight text (what Ian reads first):**")
            for h in d["highlights"][:5]:
                output.append(f"  {h}")
            output.append("")

        if d["anomalies"]:
            output.append("**Anomalies detected:**")
            for a in d["anomalies"]:
                output.append(f"- {a}")
            output.append("")

        if d["memory"]:
            output.append("**Meeting memory matches (trigger 'i remember' questions):**")
            for m in list(set(d["memory"]))[:3]:
                output.append(f"- {m}")
            output.append("")

    if lower_slides:
        output.append("## Lower Priority Flagged Slides\n")
        for num, d in lower_slides:
            flags = "; ".join(d["anomalies"][:2])
            mem_str = "; ".join(list(set(d["memory"]))[:1]) if d["memory"] else ""
            summary = flags or mem_str
            output.append(f"- **Slide {num}** ({d['title'][:60]}): {summary[:120]}")
        output.append("")

    output.append("## Clean Slides (likely skipped by Ian)\n")
    if clean_slides:
        output.append(f"Slides with no anomalies detected: {', '.join(str(s) for s in clean_slides)}")
    output.append("")

    output.append("## Slide Selection Guidance\n")
    output.append(f"- **Total flagged:** {len(ranked)} slides with anomalies or memory matches")
    output.append(f"- **Top priority:** {top_n} slides ranked by severity")
    output.append(f"- **Clean slides:** {len(clean_slides)} — likely skip")
    output.append(f"- **Ian typically questions 5-8 slides out of {len(slides)}**")
    output.append("")

    return "\n".join(output)


def main():
    if len(sys.argv) < 2:
        print("Usage: python anomaly_extract.py <path_to_deck.pdf>")
        print("\nThis script extracts slide data, detects anomalies, and generates anomaly_brief.md")
        sys.exit(1)

    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)

    print(f"Extracting slides from: {pdf_path}")
    slides = extract_slides(pdf_path)
    print(f"Found {len(slides)} slides")

    brief = generate_brief(pdf_path, slides)

    output_dir = os.path.dirname(pdf_path) or "."
    output_path = os.path.join(output_dir, "anomaly_brief.md")
    with open(output_path, "w") as f:
        f.write(brief)

    print(f"\nAnomaly brief written to: {output_path}")
    print(f"Flagged slides: {sum(1 for n in slides if detect_anomalies(n, slides[n]) or check_memory_matches(slides[n]))}")
    print(f"\nNext: Upload both the PDF and anomaly_brief.md to Claude Project")


if __name__ == "__main__":
    main()
