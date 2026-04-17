#!/usr/bin/env python3
"""
Extract Ian Ho email threads with PDF/PPTX attachments and questions.
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
OUTPUT_DIR = Path(__file__).parent / "training_data"
THREAD_IDS_FILE = Path(__file__).parent / "thread_ids.json"


def run_gws(args, suppress_stderr=True):
    """Run a gws command and return parsed JSON."""
    cmd = ["gws"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode not in (0, 1):
        return None

    # Parse output - skip keyring line
    output = result.stdout.strip()
    lines = output.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('{') or line.startswith('['):
            try:
                return json.loads('\n'.join(lines[i:]))
            except json.JSONDecodeError:
                pass
    return None


def get_all_thread_ids():
    """Get all thread IDs from Ian Ho emails with attachments."""
    if THREAD_IDS_FILE.exists():
        with open(THREAD_IDS_FILE) as f:
            return json.load(f)

    print("Fetching all thread IDs...")
    thread_ids = set()
    page_token = None
    page = 0

    while True:
        page += 1
        params = {
            "userId": "me",
            "q": f"from:{IAN_EMAIL} OR to:{IAN_EMAIL} after:2026/01/01 has:attachment",
            "maxResults": 500
        }
        if page_token:
            params["pageToken"] = page_token

        result = run_gws([
            "gmail", "users", "messages", "list",
            "--params", json.dumps(params)
        ])

        if not result:
            break

        messages = result.get("messages", [])
        for msg in messages:
            thread_ids.add(msg["threadId"])

        print(f"  Page {page}: {len(messages)} messages, {len(thread_ids)} unique threads so far")

        page_token = result.get("nextPageToken")
        if not page_token:
            break

    thread_ids = sorted(thread_ids)
    with open(THREAD_IDS_FILE, 'w') as f:
        json.dump(thread_ids, f)
    print(f"Total unique threads: {len(thread_ids)}")
    return thread_ids


def get_thread(thread_id):
    """Fetch full thread data."""
    return run_gws([
        "gmail", "users", "threads", "get",
        "--params", json.dumps({"userId": "me", "id": thread_id, "format": "full"})
    ])


def get_header(headers, name):
    """Get header value by name."""
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def extract_name_from_address(addr):
    """Extract display name from email address like 'Name <email>'."""
    match = re.match(r'^"?([^"<]+)"?\s*<', addr)
    if match:
        return match.group(1).strip()
    # If no name, use email
    match = re.match(r'<?([\w.+-]+@[\w.-]+)>?', addr)
    if match:
        return match.group(1)
    return addr.strip()


def is_ian(from_header):
    """Check if email is from Ian Ho."""
    return IAN_EMAIL.lower() in from_header.lower()


def get_body_text(payload):
    """Extract plain text body from message payload."""
    def decode_data(data):
        if not data:
            return ""
        # Fix base64url padding
        data = data.replace('-', '+').replace('_', '/')
        padding = 4 - len(data) % 4
        if padding != 4:
            data += '=' * padding
        try:
            return base64.b64decode(data).decode('utf-8', errors='replace')
        except Exception:
            return ""

    def extract_from_parts(part):
        mime = part.get("mimeType", "")
        body = part.get("body", {})

        if mime == "text/plain":
            return decode_data(body.get("data", ""))

        if mime.startswith("multipart/"):
            texts = []
            for subpart in part.get("parts", []):
                t = extract_from_parts(subpart)
                if t:
                    texts.append(t)
            return "\n".join(texts)

        return ""

    text = extract_from_parts(payload)
    if not text:
        # Try HTML as fallback
        def extract_html(part):
            mime = part.get("mimeType", "")
            body = part.get("body", {})
            if mime == "text/html":
                html = decode_data(body.get("data", ""))
                # Strip HTML tags
                return re.sub(r'<[^>]+>', '', html)
            if mime.startswith("multipart/"):
                for subpart in part.get("parts", []):
                    t = extract_html(subpart)
                    if t:
                        return t
            return ""
        text = extract_html(payload)

    return text.strip()


def find_attachments(payload, attachments=None):
    """Find all attachments in message payload."""
    if attachments is None:
        attachments = []

    filename = payload.get("filename", "")
    mime = payload.get("mimeType", "")
    body = payload.get("body", {})

    if filename:
        ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''
        if ext in ('pdf', 'pptx', 'ppt'):
            attachments.append({
                "filename": filename,
                "mimeType": mime,
                "attachmentId": body.get("attachmentId", ""),
                "size": body.get("size", 0)
            })

    for part in payload.get("parts", []):
        find_attachments(part, attachments)

    return attachments


def download_attachment(message_id, attachment_id, output_path):
    """Download an attachment."""
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

    # Fix base64url
    data = data.replace('-', '+').replace('_', '/')
    padding = 4 - len(data) % 4
    if padding != 4:
        data += '=' * padding

    try:
        decoded = base64.b64decode(data)
        with open(output_path, 'wb') as f:
            f.write(decoded)
        return True
    except Exception as e:
        print(f"    Error decoding attachment: {e}")
        return False


def clean_email_body(text):
    """Remove quoted/forwarded text from email body."""
    lines = text.split('\n')
    clean_lines = []
    for line in lines:
        # Stop at common quote markers
        stripped = line.strip()
        if re.match(r'^On .+wrote:', stripped):
            break
        if stripped.startswith('>'):
            continue
        if re.match(r'^-{3,}', stripped):
            break
        if re.match(r'^From:', stripped) and len(clean_lines) > 3:
            break
        clean_lines.append(line)
    return '\n'.join(clean_lines).strip()


def extract_questions(text):
    """Extract individual questions from text."""
    if not text:
        return []

    # Clean quoted content
    text = clean_email_body(text)

    questions = []

    # Split by numbered lists first (1. 2. etc.)
    numbered = re.split(r'\n\s*\d+[\.\)]\s+', '\n' + text)
    if len(numbered) > 2:
        # First element is preamble
        for q in numbered[1:]:
            q = q.strip()
            if q and ('?' in q or len(q) > 20):
                # Take just the first sentence/question
                questions.append(q.split('\n')[0].strip())
        if questions:
            return questions

    # Split by question marks
    sentences = re.split(r'(?<=[?])\s+', text)
    for s in sentences:
        s = s.strip()
        if '?' in s and len(s) > 10:
            questions.append(s)

    if not questions and len(text) > 20:
        # Return the whole text as one item
        questions.append(text[:500])

    return questions


def has_questions(text):
    """Check if text contains questions."""
    if not text:
        return False
    clean = clean_email_body(text)
    return '?' in clean


def assign_topic_tags(subject, body_snippets):
    """Assign topic tags based on content."""
    combined = (subject + ' ' + ' '.join(body_snippets)).lower()

    tag_patterns = {
        'marketplace': ['marketplace', 'market place'],
        'gmv': ['gmv', 'gross merchandise value'],
        'logistics': ['logistic', 'shipping', 'delivery', 'fulfillment'],
        'seller-acquisition': ['seller acquisition', 'seller onboard', 'new seller'],
        'buyer-retention': ['buyer retention', 'repeat buyer', 'cohort', 'retention'],
        'finance': ['finance', 'p&l', 'profit', 'revenue', 'cost', 'margin', 'budget', 'financial'],
        'ops-review': ['ops review', 'operations review', 'operational'],
        'strategy': ['strategy', 'strategic', 'roadmap', 'initiative'],
        'product-launch': ['product launch', 'new product', 'launch'],
        'quarterly-review': ['quarterly', 'q1', 'q2', 'q3', 'q4', 'quarter'],
        'team-performance': ['team performance', 'kpi', 'performance review', 'headcount'],
        'growth': ['growth', 'expansion'],
        'marketing': ['marketing', 'campaign', 'promotion', 'voucher'],
        'user-growth': ['user growth', 'new user', 'acquisition', 'dau', 'mau'],
        'category': ['category', 'vertical'],
        'pricing': ['pricing', 'price'],
        'supply-chain': ['supply chain', 'vendor', 'procurement'],
        'data-analysis': ['data', 'analysis', 'analytics', 'metric', 'insight'],
        'regional': ['regional', 'region', 'country', 'market'],
        'shopee': ['shopee'],
        'sea': ['sea group', 'sea limited'],
        'garena': ['garena'],
        'seabank': ['seabank', 'sea bank'],
        'e-commerce': ['e-commerce', 'ecommerce'],
        'tech': ['tech', 'engineering', 'platform', 'infrastructure'],
        'hiring': ['hiring', 'recruitment', 'headcount'],
        'business-review': ['business review', 'br ', 'weekly review', 'monthly review'],
    }

    tags = []
    for tag, patterns in tag_patterns.items():
        for pat in patterns:
            if pat in combined:
                tags.append(tag)
                break

    # Ensure at least 2 tags
    if not tags:
        tags = ['business-review', 'strategy']
    elif len(tags) < 2:
        tags.append('business-review')

    return tags[:5]


def process_thread(thread_data, thread_num):
    """Process a single thread and return structured data or None."""
    messages = thread_data.get("messages", [])
    if not messages:
        return None

    # Get subject
    first_msg = messages[0]
    headers = first_msg.get("payload", {}).get("headers", [])
    subject = get_header(headers, "Subject")

    # Check all messages for PDF/PPTX attachments
    all_attachments = []
    for msg in messages:
        atts = find_attachments(msg.get("payload", {}))
        for att in atts:
            att["message_id"] = msg["id"]
        all_attachments.extend(atts)

    if not all_attachments:
        return None

    # Check if Ian Ho is involved and asked questions
    ian_asked = False
    ian_in_thread = False

    for msg in messages:
        msg_headers = msg.get("payload", {}).get("headers", [])
        from_addr = get_header(msg_headers, "From")
        to_addr = get_header(msg_headers, "To")
        cc_addr = get_header(msg_headers, "Cc")

        if is_ian(from_addr) or is_ian(to_addr) or is_ian(cc_addr):
            ian_in_thread = True

        if is_ian(from_addr):
            body = get_body_text(msg.get("payload", {}))
            if has_questions(body):
                ian_asked = True

    if not ian_in_thread or not ian_asked:
        return None

    # Get thread date
    date_ms = int(first_msg.get("internalDate", 0))
    thread_date = datetime.fromtimestamp(date_ms / 1000).strftime("%Y-%m-%d")

    # Find the main PDF/PPTX (prefer the one that was discussed - last one or largest)
    # Group by filename to get the latest version
    att_by_name = {}
    for att in all_attachments:
        name = att["filename"]
        if name not in att_by_name or att["size"] > att_by_name[name]["size"]:
            att_by_name[name] = att

    # Pick the main deck (prefer .pdf, then .pptx, prefer larger)
    main_att = None
    for att in sorted(att_by_name.values(), key=lambda x: x["size"], reverse=True):
        ext = att["filename"].lower().rsplit('.', 1)[-1]
        if ext in ('pdf', 'pptx', 'ppt'):
            main_att = att
            break

    if not main_att:
        return None

    # Build Q&A thread
    qa_turns = []
    turn_num = 0
    q_counter = 0

    # Track responders
    responders = set()

    for msg in messages:
        msg_headers = msg.get("payload", {}).get("headers", [])
        from_addr = get_header(msg_headers, "From")
        sender_name = extract_name_from_address(from_addr)

        if not is_ian(from_addr):
            responders.add(sender_name)

        body = get_body_text(msg.get("payload", {}))
        if not body:
            continue

        clean_body = clean_email_body(body)
        if not clean_body or len(clean_body) < 10:
            continue

        if is_ian(from_addr) and has_questions(clean_body):
            turn_num += 1
            is_first_ian_turn = (turn_num == 1 and not qa_turns)

            questions = extract_questions(clean_body)
            if not questions:
                continue

            content = []
            for q in questions:
                q_counter += 1
                # Check if this is a follow-up (after at least one answer turn)
                has_answer_before = any(t["type"] == "answers" for t in qa_turns)
                q_id = f"Q{q_counter}"

                content.append({
                    "question_id": q_id,
                    "question": q
                })

            qa_turns.append({
                "turn": len(qa_turns) + 1,
                "from": IAN_NAME,
                "type": "initial_questions" if not any(t["type"] in ("answers", "initial_questions") for t in qa_turns) else "follow_up_questions",
                "content": content
            })

        elif not is_ian(from_addr) and clean_body and len(clean_body) > 20:
            # Answer turn
            # Try to map to questions
            content = []
            unanswered = [
                item
                for t in qa_turns if t["type"] in ("initial_questions", "follow_up_questions")
                for item in t["content"]
                if not any(
                    a_item.get("question_id") == item["question_id"]
                    for at in qa_turns if at["type"] == "answers"
                    for a_item in at["content"]
                )
            ]

            if unanswered:
                # Split answer text into parts for each question
                answer_text = clean_body
                if len(unanswered) == 1:
                    content = [{
                        "question_id": unanswered[0]["question_id"],
                        "answer": answer_text[:2000]
                    }]
                else:
                    # Try to split by numbered sections
                    parts = re.split(r'\n\s*\d+[\.\)]\s+', '\n' + answer_text)
                    if len(parts) > len(unanswered):
                        parts = parts[1:]  # skip preamble

                    for i, q in enumerate(unanswered):
                        ans = parts[i].strip() if i < len(parts) else answer_text[:500]
                        content.append({
                            "question_id": q["question_id"],
                            "answer": ans[:2000]
                        })
            else:
                content = [{
                    "question_id": "context",
                    "answer": clean_body[:2000]
                }]

            if content:
                qa_turns.append({
                    "turn": len(qa_turns) + 1,
                    "from": sender_name,
                    "type": "answers",
                    "content": content
                })

    if not qa_turns:
        return None

    # Collect text snippets for tagging
    snippets = [subject]
    for t in qa_turns:
        for item in t["content"]:
            snippets.append(item.get("question", item.get("answer", ""))[:200])

    tags = assign_topic_tags(subject, snippets)

    thread_id = f"thread-{thread_num:03d}"

    return {
        "thread_id": thread_id,
        "subject": subject,
        "date": thread_date,
        "deck_filename": main_att["filename"],
        "deck_topic_tags": tags,
        "deck_summary": "",
        "participants": {
            "questioner": IAN_NAME,
            "responders": sorted(responders)
        },
        "qa_thread": qa_turns,
        "attachment": main_att  # temp, removed before saving
    }


def main():
    print("=" * 60)
    print("Ian Ho Email Thread Extractor")
    print("=" * 60)

    OUTPUT_DIR.mkdir(exist_ok=True)

    # Step 1: Get all thread IDs
    thread_ids = get_all_thread_ids()
    print(f"\nProcessing {len(thread_ids)} threads...")

    # Step 2: Process each thread
    qualifying = []
    processed = 0

    # Check for resume file
    resume_file = Path(__file__).parent / "processed_threads.json"
    already_done = {}
    if resume_file.exists():
        with open(resume_file) as f:
            already_done = json.load(f)
        print(f"Resuming: {len(already_done)} threads already processed")

    for tid in thread_ids:
        processed += 1
        if processed % 50 == 0:
            print(f"  Progress: {processed}/{len(thread_ids)}, qualifying: {len(qualifying)}")

        if tid in already_done:
            if already_done[tid]:
                qualifying.append(already_done[tid])
            continue

        thread_data = get_thread(tid)
        if not thread_data:
            already_done[tid] = None
            continue

        result = process_thread(thread_data, len(qualifying) + 1)
        if result:
            qualifying.append(result)
            already_done[tid] = result
            print(f"  ✓ Thread {result['thread_id']}: {result['subject'][:60]}")
        else:
            already_done[tid] = None

        # Save progress every 20
        if processed % 20 == 0:
            with open(resume_file, 'w') as f:
                json.dump(already_done, f)

    # Save final progress
    with open(resume_file, 'w') as f:
        json.dump(already_done, f)

    print(f"\n{'=' * 60}")
    print(f"Found {len(qualifying)} qualifying threads")
    print("=" * 60)

    if not qualifying:
        print("No qualifying threads found.")
        return

    # Re-number chronologically
    qualifying.sort(key=lambda x: x["date"])
    for i, t in enumerate(qualifying):
        t["thread_id"] = f"thread-{i+1:03d}"

    # Step 3: Download attachments and write metadata
    all_tags = set()
    index_entries = []

    for t in qualifying:
        tid = t["thread_id"]
        thread_dir = OUTPUT_DIR / tid
        thread_dir.mkdir(exist_ok=True)

        # Download attachment
        att = t.pop("attachment")
        deck_path = thread_dir / att["filename"]

        if att.get("attachmentId") and not deck_path.exists():
            print(f"  Downloading {att['filename']} for {tid}...")
            success = download_attachment(att["message_id"], att["attachmentId"], deck_path)
            if not success:
                print(f"    WARNING: Failed to download {att['filename']}")

        # Build metadata
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

        # Write metadata.json
        meta_path = thread_dir / "metadata.json"
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"  ✓ {tid}: {t['subject'][:50]} ({len(t['qa_thread'])} turns)")

        all_tags.update(t["deck_topic_tags"])
        index_entries.append({
            "id": tid,
            "subject": t["subject"],
            "date": t["date"],
            "tags": t["deck_topic_tags"],
            "num_turns": len(t["qa_thread"])
        })

    # Write index.json
    dates = [e["date"] for e in index_entries]
    index = {
        "total_threads": len(qualifying),
        "date_range": {
            "from": min(dates),
            "to": max(dates)
        },
        "all_tags": sorted(all_tags),
        "threads": index_entries
    }

    index_path = OUTPUT_DIR / "index.json"
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print(f"Done! Output in: {OUTPUT_DIR}")
    print(f"Total threads: {len(qualifying)}")
    print(f"Index: {index_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
