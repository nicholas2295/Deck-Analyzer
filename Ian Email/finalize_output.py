#!/usr/bin/env python3
"""
Finalize training_data output from already-processed threads.
Reads processed_threads.json, creates folder structure,
downloads attachments, writes metadata.json and index.json.
"""

import json
import os
import re
import base64
import subprocess
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "training_data"
PROCESSED_FILE = Path(__file__).parent / "processed_threads.json"

IAN_EMAIL = "hoi@sea.com"
IAN_NAME = "Ian Ho"


def run_gws(args):
    """Run a gws command and return parsed JSON."""
    cmd = ["gws"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode not in (0, 1):
        print(f"    gws error (rc={result.returncode}): {result.stderr[:200]}")
        return None

    output = result.stdout.strip()
    lines = output.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('{') or line.startswith('['):
            try:
                return json.loads('\n'.join(lines[i:]))
            except json.JSONDecodeError:
                pass
    return None


def download_attachment(message_id, attachment_id, output_path):
    """Download an attachment via gws."""
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

    # Fix base64url encoding
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
        print(f"    Decode error: {e}")
        return False


def main():
    print("=" * 60)
    print("Ian Ho Training Data Finalizer")
    print("=" * 60)

    if not PROCESSED_FILE.exists():
        print(f"ERROR: {PROCESSED_FILE} not found. Run extract_ian_threads.py first.")
        return

    with open(PROCESSED_FILE) as f:
        processed = json.load(f)

    # Collect qualifying threads
    qualifying = [v for v in processed.values() if v is not None]
    print(f"Qualifying threads: {len(qualifying)}")

    # Sort chronologically (by date, then subject as tiebreak)
    qualifying.sort(key=lambda x: (x["date"], x["subject"]))

    # Re-number
    for i, t in enumerate(qualifying):
        t["thread_id"] = f"thread-{i+1:03d}"

    OUTPUT_DIR.mkdir(exist_ok=True)

    all_tags = set()
    index_entries = []
    failed_downloads = []

    for t in qualifying:
        tid = t["thread_id"]
        thread_dir = OUTPUT_DIR / tid
        thread_dir.mkdir(exist_ok=True)

        att = t.get("attachment", {})
        deck_filename = t.get("deck_filename", "")

        # Download attachment if not already present
        deck_path = thread_dir / deck_filename if deck_filename else None
        downloaded = False

        if att and att.get("attachmentId") and deck_filename:
            if deck_path and not deck_path.exists():
                print(f"  [{tid}] Downloading: {deck_filename[:50]}...")
                success = download_attachment(
                    att["message_id"],
                    att["attachmentId"],
                    deck_path
                )
                if success:
                    size_kb = os.path.getsize(deck_path) / 1024
                    print(f"    OK ({size_kb:.0f} KB)")
                    downloaded = True
                else:
                    print(f"    FAILED to download {deck_filename}")
                    failed_downloads.append(f"{tid}: {deck_filename}")
            else:
                print(f"  [{tid}] Already exists: {deck_filename[:50]}")
                downloaded = True

        # Build metadata (excluding internal 'attachment' field)
        metadata = {
            "id": tid,
            "subject": t["subject"],
            "date": t["date"],
            "deck_filename": deck_filename,
            "deck_topic_tags": t["deck_topic_tags"],
            "deck_summary": t.get("deck_summary", ""),
            "participants": t["participants"],
            "qa_thread": t["qa_thread"]
        }

        # Write metadata.json
        meta_path = thread_dir / "metadata.json"
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        tags = t["deck_topic_tags"]
        all_tags.update(tags)

        index_entries.append({
            "id": tid,
            "subject": t["subject"],
            "date": t["date"],
            "tags": tags,
            "num_turns": len(t["qa_thread"])
        })

        turns = len(t["qa_thread"])
        q_count = sum(
            len(turn["content"])
            for turn in t["qa_thread"]
            if turn["type"] in ("initial_questions", "follow_up_questions")
        )
        print(f"  [{tid}] {t['date']} | {t['subject'][:50]:50} | {turns} turns, {q_count} Qs")

    # Write index.json
    dates = [e["date"] for e in index_entries]
    index = {
        "total_threads": len(qualifying),
        "date_range": {
            "from": min(dates) if dates else "",
            "to": max(dates) if dates else ""
        },
        "all_tags": sorted(all_tags),
        "threads": index_entries
    }

    index_path = OUTPUT_DIR / "index.json"
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 60)
    print(f"Done!")
    print(f"  Threads written : {len(qualifying)}")
    print(f"  Output directory: {OUTPUT_DIR}")
    print(f"  Index file      : {index_path}")
    if failed_downloads:
        print(f"\n  FAILED downloads ({len(failed_downloads)}):")
        for fd in failed_downloads:
            print(f"    - {fd}")
    print("=" * 60)


if __name__ == "__main__":
    main()
