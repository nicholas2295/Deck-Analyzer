#!/usr/bin/env python3
"""
Extract Ian Ho email threads (2025) with PDF/PPTX attachments and questions.
Time range: Jan 1 2025 – Dec 31 2025
Output: training_data_2025/
"""

import json
import os
import re
import base64
import subprocess
import sys
from datetime import datetime
from pathlib import Path

IAN_EMAIL = "hoi@sea.com"
IAN_NAME = "Ian Ho"
OUTPUT_DIR = Path(__file__).parent / "training_data_2025"
THREAD_IDS_FILE = Path(__file__).parent / "thread_ids_2025.json"
PROCESSED_FILE = Path(__file__).parent / "processed_threads_2025.json"

QUERY = f"from:{IAN_EMAIL} OR to:{IAN_EMAIL} after:2025/01/01 before:2026/01/01 has:attachment"


# ─── gws helpers ─────────────────────────────────────────────────────────────

def run_gws(args):
    """Run a gws command and return parsed JSON, or None on failure."""
    cmd = ["gws"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode not in (0, 1):
        return None
    output = result.stdout.strip()
    for i, line in enumerate(output.split('\n')):
        if line.startswith('{') or line.startswith('['):
            try:
                return json.loads('\n'.join(output.split('\n')[i:]))
            except json.JSONDecodeError:
                pass
    return None


def get_all_thread_ids():
    """Fetch thread IDs for all Ian emails with attachments in 2025."""
    if THREAD_IDS_FILE.exists():
        with open(THREAD_IDS_FILE) as f:
            ids = json.load(f)
        print(f"Loaded {len(ids)} thread IDs from cache.")
        return ids

    print("Fetching thread IDs from Gmail...")
    thread_ids = set()
    page_token = None
    page = 0

    while True:
        page += 1
        params = {"userId": "me", "q": QUERY, "maxResults": 500}
        if page_token:
            params["pageToken"] = page_token

        result = run_gws([
            "gmail", "users", "messages", "list",
            "--params", json.dumps(params)
        ])
        if not result:
            break

        for msg in result.get("messages", []):
            thread_ids.add(msg["threadId"])

        print(f"  Page {page}: {len(result.get('messages', []))} msgs, "
              f"{len(thread_ids)} unique threads so far")

        page_token = result.get("nextPageToken")
        if not page_token:
            break

    ids = sorted(thread_ids)
    with open(THREAD_IDS_FILE, 'w') as f:
        json.dump(ids, f)
    print(f"Saved {len(ids)} thread IDs.")
    return ids


def get_thread(thread_id):
    return run_gws([
        "gmail", "users", "threads", "get",
        "--params", json.dumps({"userId": "me", "id": thread_id, "format": "full"})
    ])


# ─── parsing helpers ──────────────────────────────────────────────────────────

def get_header(headers, name):
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def extract_name_from_address(addr):
    m = re.match(r'^"?([^"<]+)"?\s*<', addr)
    if m:
        return m.group(1).strip()
    m = re.match(r'<?([\w.+-]+@[\w.-]+)>?', addr)
    if m:
        return m.group(1)
    return addr.strip()


def is_ian(from_header):
    return IAN_EMAIL.lower() in from_header.lower()


def decode_b64(data):
    if not data:
        return ""
    data = data.replace('-', '+').replace('_', '/')
    pad = 4 - len(data) % 4
    if pad != 4:
        data += '=' * pad
    try:
        return base64.b64decode(data).decode('utf-8', errors='replace')
    except Exception:
        return ""


def get_body_text(payload):
    """Extract plain text (falling back to stripped HTML) from a message payload."""
    def from_parts(part):
        mime = part.get("mimeType", "")
        body = part.get("body", {})
        if mime == "text/plain":
            return decode_b64(body.get("data", ""))
        if mime.startswith("multipart/"):
            texts = [from_parts(p) for p in part.get("parts", [])]
            return "\n".join(t for t in texts if t)
        return ""

    text = from_parts(payload)
    if not text:
        def from_html(part):
            mime = part.get("mimeType", "")
            body = part.get("body", {})
            if mime == "text/html":
                html = decode_b64(body.get("data", ""))
                return re.sub(r'<[^>]+>', '', html)
            if mime.startswith("multipart/"):
                for p in part.get("parts", []):
                    t = from_html(p)
                    if t:
                        return t
            return ""
        text = from_html(payload)
    return text.strip()


def find_attachments(payload, result=None):
    """Recursively find all PDF/PPTX attachments in a message payload."""
    if result is None:
        result = []
    filename = payload.get("filename", "")
    if filename:
        ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''
        if ext in ('pdf', 'pptx', 'ppt'):
            body = payload.get("body", {})
            result.append({
                "filename": filename,
                "mimeType": payload.get("mimeType", ""),
                "attachmentId": body.get("attachmentId", ""),
                "size": body.get("size", 0)
            })
    for part in payload.get("parts", []):
        find_attachments(part, result)
    return result


def download_attachment(message_id, attachment_id, output_path):
    result = run_gws([
        "gmail", "users", "messages", "attachments", "get",
        "--params", json.dumps({
            "userId": "me",
            "messageId": message_id,
            "id": attachment_id
        })
    ])
    if not result:
        return False
    data = result.get("data", "")
    if not data:
        return False
    try:
        raw = decode_b64(data)
        # decode_b64 returns str; we need bytes
        data2 = data.replace('-', '+').replace('_', '/')
        pad = 4 - len(data2) % 4
        if pad != 4:
            data2 += '=' * pad
        decoded = base64.b64decode(data2)
        with open(output_path, 'wb') as f:
            f.write(decoded)
        return True
    except Exception as e:
        print(f"    Decode error: {e}")
        return False


# ─── text analysis ────────────────────────────────────────────────────────────

def clean_email_body(text):
    """Strip quoted/forwarded content."""
    lines = text.split('\n')
    clean = []
    for line in lines:
        s = line.strip()
        if re.match(r'^On .+wrote:', s):
            break
        if s.startswith('>'):
            continue
        if re.match(r'^-{3,}', s):
            break
        if re.match(r'^From:', s) and len(clean) > 3:
            break
        clean.append(line)
    return '\n'.join(clean).strip()


def has_questions(text):
    return bool(text) and '?' in clean_email_body(text)


def extract_questions(text):
    """Split text into individual question strings."""
    text = clean_email_body(text)
    if not text:
        return []

    questions = []

    # Try numbered list first: "1. ...\n2. ..."
    numbered = re.split(r'\n\s*\d+[\.\)]\s+', '\n' + text)
    if len(numbered) > 2:
        for q in numbered[1:]:
            q = q.strip()
            if q and ('?' in q or len(q) > 20):
                questions.append(q.split('\n')[0].strip())
        if questions:
            return questions

    # Split on question marks
    sentences = re.split(r'(?<=[?])\s+', text)
    for s in sentences:
        s = s.strip()
        if '?' in s and len(s) > 10:
            questions.append(s)

    if not questions and len(text) > 20:
        questions.append(text[:500])

    return questions


def assign_topic_tags(subject, snippets):
    combined = (subject + ' ' + ' '.join(snippets)).lower()
    tag_patterns = {
        'marketplace':       ['marketplace', 'market place'],
        'gmv':               ['gmv', 'gross merchandise value'],
        'logistics':         ['logistic', 'shipping', 'delivery', 'fulfillment'],
        'seller-acquisition':['seller acquisition', 'seller onboard', 'new seller'],
        'buyer-retention':   ['buyer retention', 'repeat buyer', 'cohort', 'retention'],
        'finance':           ['finance', 'p&l', 'profit', 'revenue', 'cost', 'margin',
                              'budget', 'financial', 'fp&a'],
        'ops-review':        ['ops review', 'operations review', 'operational'],
        'strategy':          ['strategy', 'strategic', 'roadmap', 'initiative'],
        'product-launch':    ['product launch', 'new product', 'launch'],
        'quarterly-review':  ['quarterly', 'q1', 'q2', 'q3', 'q4', 'quarter'],
        'team-performance':  ['team performance', 'kpi', 'performance review', 'headcount'],
        'growth':            ['growth', 'expansion'],
        'marketing':         ['marketing', 'campaign', 'promotion', 'voucher'],
        'user-growth':       ['user growth', 'new user', 'acquisition', 'dau', 'mau'],
        'category':          ['category', 'vertical'],
        'pricing':           ['pricing', 'price'],
        'supply-chain':      ['supply chain', 'vendor', 'procurement'],
        'data-analysis':     ['data', 'analysis', 'analytics', 'metric', 'insight'],
        'regional':          ['regional', 'region', 'country', 'market'],
        'shopee':            ['shopee'],
        'sea':               ['sea group', 'sea limited'],
        'garena':            ['garena'],
        'seabank':           ['seabank', 'sea bank'],
        'e-commerce':        ['e-commerce', 'ecommerce'],
        'tech':              ['tech', 'engineering', 'platform', 'infrastructure'],
        'hiring':            ['hiring', 'recruitment', 'headcount'],
        'business-review':   ['business review', 'weekly review', 'monthly review',
                              'bi-weekly', 'biweekly'],
        'cross-border':      ['cross border', 'cross-border', 'cb ', 'cntw', 'cnls',
                              'krjp', 'kr/jp'],
        'sip':               ['sip '],
        'townhall':          ['townhall', 'town hall'],
    }
    tags = []
    for tag, patterns in tag_patterns.items():
        for pat in patterns:
            if pat in combined:
                tags.append(tag)
                break
    if not tags:
        tags = ['business-review', 'strategy']
    elif len(tags) < 2:
        tags.append('business-review')
    return tags[:5]


# ─── thread processing ────────────────────────────────────────────────────────

def process_thread(thread_data):
    """
    Returns a structured dict for a qualifying thread, or None.
    Qualifying = has PDF/PPTX attachment AND Ian asked at least one question.
    """
    messages = thread_data.get("messages", [])
    if not messages:
        return None

    first_msg = messages[0]
    headers = first_msg.get("payload", {}).get("headers", [])
    subject = get_header(headers, "Subject")

    # Collect all PDF/PPTX attachments across all messages
    all_attachments = []
    for msg in messages:
        atts = find_attachments(msg.get("payload", {}))
        for att in atts:
            att["message_id"] = msg["id"]
        all_attachments.extend(atts)

    if not all_attachments:
        return None

    # Check Ian involvement and questions
    ian_in_thread = False
    ian_asked = False
    for msg in messages:
        h = msg.get("payload", {}).get("headers", [])
        frm = get_header(h, "From")
        to  = get_header(h, "To")
        cc  = get_header(h, "Cc")
        if is_ian(frm) or is_ian(to) or is_ian(cc):
            ian_in_thread = True
        if is_ian(frm):
            body = get_body_text(msg.get("payload", {}))
            if has_questions(body):
                ian_asked = True

    if not ian_in_thread or not ian_asked:
        return None

    # Pick the "main" deck: prefer largest PDF, fall back to largest PPTX
    att_by_name = {}
    for att in all_attachments:
        n = att["filename"]
        if n not in att_by_name or att["size"] > att_by_name[n]["size"]:
            att_by_name[n] = att

    main_att = None
    for att in sorted(att_by_name.values(), key=lambda x: x["size"], reverse=True):
        if att["filename"].lower().rsplit('.', 1)[-1] in ('pdf', 'pptx', 'ppt'):
            main_att = att
            break
    if not main_att:
        return None

    # Thread date
    date_ms = int(first_msg.get("internalDate", 0))
    thread_date = datetime.fromtimestamp(date_ms / 1000).strftime("%Y-%m-%d")

    # Build Q&A turns
    qa_turns = []
    q_counter = 0
    responders = set()

    for msg in messages:
        h = msg.get("payload", {}).get("headers", [])
        frm = get_header(h, "From")
        sender_name = extract_name_from_address(frm)

        if not is_ian(frm):
            responders.add(sender_name)

        body = get_body_text(msg.get("payload", {}))
        if not body:
            continue
        clean = clean_email_body(body)
        if not clean or len(clean) < 10:
            continue

        if is_ian(frm) and has_questions(clean):
            questions = extract_questions(clean)
            if not questions:
                continue

            content = []
            has_prior_answers = any(t["type"] == "answers" for t in qa_turns)

            for q in questions:
                q_counter += 1
                content.append({
                    "question_id": f"Q{q_counter}",
                    "question": q
                })

            turn_type = (
                "initial_questions"
                if not any(t["type"] in ("answers", "initial_questions") for t in qa_turns)
                else "follow_up_questions"
            )
            qa_turns.append({
                "turn": len(qa_turns) + 1,
                "from": IAN_NAME,
                "type": turn_type,
                "content": content
            })

        elif not is_ian(frm) and len(clean) > 20:
            # Map answer to unanswered questions
            already_answered_ids = {
                item["question_id"]
                for t in qa_turns if t["type"] == "answers"
                for item in t["content"]
            }
            unanswered = [
                item
                for t in qa_turns
                if t["type"] in ("initial_questions", "follow_up_questions")
                for item in t["content"]
                if item["question_id"] not in already_answered_ids
            ]

            if unanswered:
                if len(unanswered) == 1:
                    content = [{
                        "question_id": unanswered[0]["question_id"],
                        "answer": clean[:2000]
                    }]
                else:
                    parts = re.split(r'\n\s*\d+[\.\)]\s+', '\n' + clean)
                    if len(parts) > 1:
                        parts = parts[1:]
                    content = []
                    for i, q in enumerate(unanswered):
                        ans = parts[i].strip() if i < len(parts) else clean[:500]
                        content.append({
                            "question_id": q["question_id"],
                            "answer": ans[:2000]
                        })
            else:
                content = [{"question_id": "context", "answer": clean[:2000]}]

            if content:
                qa_turns.append({
                    "turn": len(qa_turns) + 1,
                    "from": sender_name,
                    "type": "answers",
                    "content": content
                })

    if not qa_turns:
        return None

    snippets = [subject] + [
        item.get("question", item.get("answer", ""))[:200]
        for t in qa_turns for item in t["content"]
    ]

    return {
        "subject": subject,
        "date": thread_date,
        "deck_filename": main_att["filename"],
        "deck_topic_tags": assign_topic_tags(subject, snippets),
        "deck_summary": "",
        "participants": {
            "questioner": IAN_NAME,
            "responders": sorted(responders)
        },
        "qa_thread": qa_turns,
        "_attachment": main_att   # internal, stripped before saving
    }


# ─── main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Ian Ho 2025 Email Thread Extractor")
    print("=" * 60)

    OUTPUT_DIR.mkdir(exist_ok=True)

    # Phase 1: get thread IDs
    thread_ids = get_all_thread_ids()
    total = len(thread_ids)
    print(f"\nProcessing {total} threads...")

    # Phase 2: process threads (with resume support)
    already_done = {}
    if PROCESSED_FILE.exists():
        with open(PROCESSED_FILE) as f:
            already_done = json.load(f)
        done_count = len(already_done)
        qualifying_count = sum(1 for v in already_done.values() if v)
        print(f"Resuming: {done_count}/{total} processed, {qualifying_count} qualifying so far")

    qualifying = []
    for i, already in already_done.items():
        if already:
            qualifying.append(already)

    processed = 0
    for tid in thread_ids:
        if tid in already_done:
            processed += 1
            continue

        processed += 1
        if processed % 50 == 0:
            pct = processed / total * 100
            print(f"  {processed}/{total} ({pct:.0f}%) — {len(qualifying)} qualifying")

        thread_data = get_thread(tid)
        if not thread_data:
            already_done[tid] = None
        else:
            result = process_thread(thread_data)
            if result:
                qualifying.append(result)
                already_done[tid] = result
                print(f"  ✓ {result['date']} | {result['subject'][:55]}")
            else:
                already_done[tid] = None

        if processed % 20 == 0:
            with open(PROCESSED_FILE, 'w') as f:
                json.dump(already_done, f)

    with open(PROCESSED_FILE, 'w') as f:
        json.dump(already_done, f)

    print(f"\nFound {len(qualifying)} qualifying threads.")

    if not qualifying:
        print("Nothing to write.")
        return

    # Phase 3: sort chronologically and write output
    qualifying.sort(key=lambda x: (x["date"], x["subject"]))
    for i, t in enumerate(qualifying):
        t["_thread_id"] = f"thread-{i+1:03d}"

    all_tags = set()
    index_entries = []
    failed = []

    for t in qualifying:
        tid = t["_thread_id"]
        thread_dir = OUTPUT_DIR / tid
        thread_dir.mkdir(exist_ok=True)

        att = t.pop("_attachment")
        deck_path = thread_dir / att["filename"]

        if att.get("attachmentId") and not deck_path.exists():
            print(f"  [{tid}] Downloading {att['filename'][:55]}...")
            ok = download_attachment(att["message_id"], att["attachmentId"], deck_path)
            if ok:
                kb = os.path.getsize(deck_path) / 1024
                print(f"    OK ({kb:.0f} KB)")
            else:
                print(f"    FAILED")
                failed.append(f"{tid}: {att['filename']}")
        else:
            size = deck_path.stat().st_size // 1024 if deck_path.exists() else 0
            print(f"  [{tid}] Exists ({size} KB): {att['filename'][:55]}")

        metadata = {
            "id": tid,
            "subject": t["subject"],
            "date": t["date"],
            "deck_filename": t["deck_filename"],
            "deck_topic_tags": t["deck_topic_tags"],
            "deck_summary": t["deck_summary"],
            "participants": t["participants"],
            "qa_thread": t["qa_thread"]
        }
        with open(thread_dir / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        all_tags.update(t["deck_topic_tags"])
        turns = len(t["qa_thread"])
        q_count = sum(
            len(turn["content"])
            for turn in t["qa_thread"]
            if turn["type"] in ("initial_questions", "follow_up_questions")
        )
        index_entries.append({
            "id": tid,
            "subject": t["subject"],
            "date": t["date"],
            "tags": t["deck_topic_tags"],
            "num_turns": turns
        })
        print(f"  [{tid}] {t['date']} | {t['subject'][:50]:50} | {turns} turns, {q_count} Qs")

    dates = [e["date"] for e in index_entries]
    index = {
        "total_threads": len(qualifying),
        "date_range": {"from": min(dates), "to": max(dates)},
        "all_tags": sorted(all_tags),
        "threads": index_entries
    }
    with open(OUTPUT_DIR / "index.json", 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 60)
    print(f"Done!  {len(qualifying)} threads  →  {OUTPUT_DIR}")
    if failed:
        print(f"  {len(failed)} download failures:")
        for fd in failed:
            print(f"    - {fd}")
    print("=" * 60)


if __name__ == "__main__":
    main()
