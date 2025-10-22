#!/usr/bin/env python3
"""
Cache markdown descriptions for AI Engineer roles using r.jina.ai proxy.
Allows resuming by skipping job IDs that already have cached files.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import requests

DETAIL_DIR = Path("data/job_details")
DETAIL_DIR.mkdir(parents=True, exist_ok=True)

JOB_LIST_PATH = Path("data/seek_ai_engineer_jobs.json")
JOB_DETAIL_URL = "https://r.jina.ai/https://www.seek.com.au/job/{job_id}"
DELAY_SECONDS = 0.6
TIMEOUT = 25
MAX_ATTEMPTS = 4
BACKOFF_SECONDS = 30


def load_jobs() -> list[dict]:
    if not JOB_LIST_PATH.exists():
        raise SystemExit("AI job listing file not found. Run seek_job_analysis.py once first.")
    return json.loads(JOB_LIST_PATH.read_text())


def cache_details() -> None:
    jobs = load_jobs()
    remaining = sum(1 for job in jobs if not (DETAIL_DIR / f"{job['job_id']}.md").exists())
    print(f"{remaining} job descriptions to fetch")

    for idx, job in enumerate(jobs, start=1):
        job_id = job["job_id"]
        path = DETAIL_DIR / f"{job_id}.md"
        if path.exists():
            continue

        attempt = 0
        while attempt < MAX_ATTEMPTS:
            attempt += 1
            url = JOB_DETAIL_URL.format(job_id=job_id)
            try:
                resp = requests.get(url, timeout=TIMEOUT)
            except requests.RequestException as exc:
                print(f"[{idx}/{len(jobs)}] {job_id}: attempt {attempt} failed ({exc})")
                time.sleep(BACKOFF_SECONDS)
                continue

            if resp.status_code == 200 and resp.text.strip():
                path.write_text(resp.text)
                if idx % 20 == 0:
                    print(f"[{idx}/{len(jobs)}] cached {job_id}")
                time.sleep(DELAY_SECONDS)
                break

            if resp.status_code == 429:
                print(f"[{idx}/{len(jobs)}] {job_id}: 429 rate limited (attempt {attempt}), backing off")
                time.sleep(BACKOFF_SECONDS)
                continue

            print(f"[{idx}/{len(jobs)}] {job_id}: unexpected status {resp.status_code}")
            break


if __name__ == "__main__":
    cache_details()
