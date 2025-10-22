#!/usr/bin/env python3
"""
Collect Seek job listings for given keywords and compute demand and skill trends.

Relies on a browser session cookie string supplied by the user to bypass Cloudflare.
Outputs JSON datasets for reuse and prints summary statistics for convenience.
"""

from __future__ import annotations

import json
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from http.cookies import SimpleCookie
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple
import re

import requests


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

COOKIE_BLOB = """
sol_id=b1ba265d-20ea-4c20-954e-b8d1e95f5c00; ajs_anonymous_id=be01d29974410c52cf013742e6c18a4c; _pin_unauth=dWlkPU0yRXlaVEExT0dNdE1tRmtPUzAwTTJaa0xXRXlOVGd0TkRWalpqSTROemhpWWpZeA; _ga=GA1.1.1842839793.1743374903; _cc_id=f6eb0f0618d1c3404c8c64fb6d384802; cto_bundle=zXAErl9xMjV2WXp6a3Q4cm9aaWZHcyUyRkRIZjdrQVBxa05CYXJyTjlNZUg4YnZLZHR3cVdiJTJGTngwM05mJTJGTkNIejJqdiUyQmlTTmM2TTdoTjlnQWglMkZlcnZOaSUyRmV3cjVuJTJCVkJHb0ZZJTJGZFpHOVBtVU9YRnFBcGw1c0ZmdnVSMUlDcWRoOXdncUZ0VjFBRkdRVFkyZTlQdnlDWEpwbWNRJTNEJTNE; _hjSessionUser_162402=eyJpZCI6IjZiOTdjODI2LTIwM2UtNTdhNS1iM2RkLWUxZDBiNGRhZWVhMSIsImNyZWF0ZWQiOjE3NDMzNzQ5MDMxMDksImV4aXN0aW5nIjp0cnVlfQ==; _hjSessionUser_755180=eyJpZCI6IjAxNmNkNmEzLTEyOTctNWVmNS04OTE1LWFkOWQwZmQwYjViZCIsImNyZWF0ZWQiOjE3NDMzNzU1MDE5NDQsImV4aXN0aW5nIjpmYWxzZX0=; _fbp=fb.2.1757912699792.660563107100421967; _gcl_au=1.1.568121627.1757912701; registeredCandidateId=588619448; __gads=ID=f1f2571ab52a4557:T=1743375022:RT=1757912949:S=ALNI_Mbokfc051MxWaOF5wAh_tgpWAt0-A; __gpi=UID=000010804a771f3d:T=1743375022:RT=1757912949:S=ALNI_MajZg3FK5VeNsydSutPwo3KXS_koA; __cf_bm=ueVsW4CNXqNjQTPawXf6Ku9U_mtFFEe6sCI.8cykwxo-1761027759-1.0.1.1-bAfLV5b5BYQSwQnhHuEvRLta8dxj25b8XCtIV8oK.kukrh_Mp2Qt0IEieJTNg13cHklFzlSFFaZFhOTK4vK5NroHyJJO0.ay.1O2WfKdzfs; _cfuvid=_31DA5WkhJW2tP4N6SKb1vsCygzDUVDI9BytxDQfgh8-1761027759963-0.0.1.1-604800000; da_cdt=visid_0195e93ddb7a0013e51dbc9facbd0507d001807500aee-sesid_1761027762049-hbvid_b1ba265d20ea4c20954eb8d1e95f5c00-tempAcqSessionId_1761027761334-tempAcqVisitorId_b1ba265d20ea4c20954eb8d1e95f5c00; da_anz_candi_sid=1761027762049; da_searchTerm=undefined; _hjSession_162402=eyJpZCI6IjI1MWM3NTg4LTYxMTQtNDQyMS1iNGFjLTJiMmVmZjRkYjRlZSIsImMiOjE3NjEwMjc3NjI1NDAsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=; panoramaId_expiry=1761114162299; panoramaId=262955618e4080c1b28cbf72209ea9fb927a116b55780c9bb41f96763689fd75; panoramaIdType=panoDevice; _clck=1ym81n5%5E2%5Eg0c%5E0%5E1915; g_state={"i_l":0,"i_ll":1761027807365,"i_b":"yDOSshyqPMiLHBjJW507V5i8niEt3t+zCL/M/c2J2ZY"}; skipSilentLogin=true; main=V%7C2~P%7Cjobsearch~K%7Cai%20engineer~WID%7C3000~OSF%7Cquick&set=1761027956931/V%7C2~P%7Cjobsearch~K%7Cbackend%20python%20developer~WH%7CAll%20Sydney%20NSW~WID%7C1000~W%7C242~OSF%7Cquick&set=1761027762106/V%7C2~P%7Cjobsearch~K%7Cbackend%20developer~WH%7CAll%20Sydney%20NSW~WID%7C1000~W%7C242~OSF%7Cquick&set=1757912770139; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%229YkJUGnv4mAmZ95rGbJ8%22%2C%22expiryDate%22%3A%222026-10-21T06%3A25%3A57.964Z%22%7D; _hjHasCachedUserAttributes=true; utag_main=v_id:0195e93ddb7a0013e51dbc9facbd0507d001807500aee$_sn:26$_se:18%3Bexp-session$_ss:0%3Bexp-session$_st:1761029760728%3Bexp-session$ses_id:1761027762049%3Bexp-session$_pn:6%3Bexp-session$_prevpage:search%20results%3Bexp-1761031560738; _ga_JYC9JXRYWC=GS2.1.s1761027763$o29$g1$t1761027960$j54$l0$h0; __rtbh.uid=%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%22NULL%22%2C%22expiryDate%22%3A%222026-10-21T06%3A26%3A00.784Z%22%7D; _uetsid=59bb9cc0ae4611f083bda76cd28efead; _uetvid=15a4d3200db911f089b6a1d9b0f0a0f8; JobseekerSessionId=b3e94124-bf5a-4d1b-a8d2-5206a5311254; JobseekerVisitorId=b3e94124-bf5a-4d1b-a8d2-5206a5311254; _clsk=x7s2cb%5E1761027960987%5E6%5E0%5Ek.clarity.ms%2Fcollect; hubble_temp_acq_session=id%3A1761027761334_end%3A1761029993383_sent%3A38; _dd_s=rum=0&expire=1761029217611&logs=0
""".strip()

SEARCH_URL = "https://www.seek.com.au/api/jobsearch/v5/search"
JOB_DETAIL_PROXY = "https://r.jina.ai/https://www.seek.com.au/job/{job_id}"

BASE_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en,zh-CN;q=0.9,zh;q=0.8,en-GB;q=0.7,en-US;q=0.6,en-AU;q=0.5",
    "priority": "u=1, i",
    "referer": "https://www.seek.com.au/",
    "sec-ch-ua": '"Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "seek-request-brand": "seek",
    "seek-request-country": "AU",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0",
    "x-seek-checksum": "12fc8013",
    "x-seek-site": "Chalice",
}

BASE_PARAMS = {
    "siteKey": "AU-Main",
    "sourcesystem": "houston",
    "eventCaptureSessionId": "03b3ca4e-fa0f-4cf7-b0b9-b8d04f158943",
    "userid": "03b3ca4e-fa0f-4cf7-b0b9-b8d04f158943",
    "userqueryid": "f8ad2e296a57371f161829581cd83dab-8317736",
    "usersessionid": "03b3ca4e-fa0f-4cf7-b0b9-b8d04f158943",
    "where": "All Australia",
    "pageSize": 22,
    "include": "seodata,gptTargeting,relatedsearches,asyncpills",
    "locale": "en-AU",
    "solId": "b1ba265d-20ea-4c20-954e-b8d1e95f5c00",
    "source": "FE_JDV",
    "relatedSearchesCount": 12,
    "queryHints": "spellingCorrection",
    "facets": "salaryMin,workArrangement,workType",
    "sortmode": "ListedDate",
}

# Conservative delay to avoid hammering the endpoint.
REQUEST_DELAY_SECONDS = 0.35

# Skill lexicon tuned for AI / Python engineering roles. Each entry is matched case-insensitively.
SKILL_PATTERNS = {
    "python": r"\bpython\b",
    "pytorch": r"\bpytorch\b",
    "tensorflow": r"\btensorflow\b",
    "keras": r"\bkeras\b",
    "scikit-learn": r"\bscikit[- ]learn\b",
    "pandas": r"\bpandas\b",
    "numpy": r"\bnumpy\b",
    "sql": r"\bsql\b",
    "nosql": r"\bno[- ]?sql\b",
    "spark": r"\bspark\b",
    "databricks": r"\bdatabricks\b",
    "aws": r"\baws\b",
    "azure": r"\bazure\b",
    "gcp": r"\bgoogle cloud\b|\bgcp\b",
    "docker": r"\bdocker\b",
    "kubernetes": r"\bkubernetes\b",
    "mlops": r"\bml[- ]?ops\b",
    "ci/cd": r"\bci/?cd\b",
    "git": r"\bgit\b",
    "linux": r"\blinux\b",
    "rest api": r"\brest(ful)?\s+api\b",
    "grpc": r"\bgrpc\b",
    "microservices": r"\bmicro-?services\b",
    "nlp": r"\bnatural language processing\b|\bnlp\b",
    "computer vision": r"\bcomputer vision\b",
    "reinforcement learning": r"\breinforcement learning\b",
    "machine learning": r"\bmachine learning\b",
    "deep learning": r"\bdeep learning\b",
    "generative ai": r"\bgenerative ai\b",
    "llm": r"\bllms?\b|\blarge language model\b",
    "rag": r"\brag\b|\bretrieval[- ]augmented\b",
    "prompt engineering": r"\bprompt engineering\b",
    "statistics": r"\bstatistics?\b",
    "probability": r"\bprobabilit(y|ies)\b",
    "linear algebra": r"\blinear algebra\b",
    "agile": r"\bagile\b",
    "jira": r"\bjira\b",
    "power bi": r"\bpower bi\b",
    "tableau": r"\btableau\b",
    "snowflake": r"\bsnowflake\b",
    "bigquery": r"\bbigquery\b",
    "airflow": r"\bairflow\b",
    "sql server": r"\bsql server\b",
    "postgresql": r"\bpostgres(ql)?\b",
    "mongodb": r"\bmongodb\b",
}

COLLECT_SKILLS = False
DETAIL_CACHE_DIR = Path("data/job_details")
DETAIL_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class JobRecord:
    job_id: str
    title: str
    listing_date: datetime
    location: Optional[str]
    employer: Optional[str]
    work_type: Optional[str]
    description_text: Optional[str] = None


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def parse_cookies(cookie_blob: str) -> Dict[str, str]:
    jar = SimpleCookie()
    jar.load(cookie_blob)
    return {key: morsel.value for key, morsel in jar.items()}


def iso_to_datetime(value: str) -> datetime:
    """Convert ISO 8601 timestamps (with trailing Z) to timezone-aware datetime."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def week_floor(date_obj: datetime) -> datetime:
    """Return the Monday (00:00 UTC) for the week of the provided datetime."""
    monday = date_obj - timedelta(days=date_obj.weekday())
    return datetime(monday.year, monday.month, monday.day, tzinfo=timezone.utc)


def normalise_markdown(markdown: str) -> str:
    """Lower-case and strip control characters from markdown content."""
    return " ".join(markdown.lower().split())


def extract_skills(markdown_text: str) -> Set[str]:
    text = normalise_markdown(markdown_text)
    hits: Set[str] = set()
    for label, pattern in SKILL_REGEX.items():
        if pattern.search(text):
            hits.add(label)
    return hits


def build_skill_regex() -> Dict[str, "re.Pattern[str]"]:
    return {label: re.compile(pattern, flags=re.IGNORECASE) for label, pattern in SKILL_PATTERNS.items()}


SKILL_REGEX = build_skill_regex()


# ---------------------------------------------------------------------------
# Fetch functions
# ---------------------------------------------------------------------------

def build_session() -> Tuple[requests.Session, Dict[str, str]]:
    cookies = parse_cookies(COOKIE_BLOB)
    session = requests.Session()
    session.headers.update(BASE_HEADERS)
    return session, cookies


def fetch_jobs_for_keyword(
    session: requests.Session,
    cookies: Dict[str, str],
    keyword: str,
    max_age_days: int = 90,
    max_pages: int = 160,
) -> List[JobRecord]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    results: List[JobRecord] = []
    seen_ids: Set[str] = set()
    page = 1
    reached_cutoff = False

    while page <= max_pages and not reached_cutoff:
        params = BASE_PARAMS.copy()
        params.update({"keywords": keyword, "page": page})
        response = session.get(SEARCH_URL, params=params, cookies=cookies, timeout=30)
        response.raise_for_status()
        payload = response.json()
        jobs = payload.get("data", [])

        if not jobs:
            break

        for job in jobs:
            job_id = job.get("id")
            if not job_id or job_id in seen_ids:
                continue

            listing_date_raw = job.get("listingDate")
            if not listing_date_raw:
                continue

            listing_dt = iso_to_datetime(listing_date_raw)
            if listing_dt < cutoff:
                reached_cutoff = True
                continue

            seen_ids.add(job_id)
            location = ", ".join(loc.get("label") for loc in job.get("locations", []) if loc.get("label")) or None
            work_type = ", ".join(job.get("workTypes") or []) or None
            record = JobRecord(
                job_id=job_id,
                title=job.get("title") or "",
                listing_date=listing_dt,
                location=location,
                employer=(job.get("companyName") or job.get("advertiser", {}).get("description")),
                work_type=work_type,
            )
            results.append(record)

        page += 1
        time.sleep(REQUEST_DELAY_SECONDS)

    return results


def fetch_job_markdown(job_id: str, timeout: int = 30) -> Optional[str]:
    url = JOB_DETAIL_PROXY.format(job_id=job_id)
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200 and resp.text.strip():
            return resp.text
        return None
    except requests.RequestException:
        return None


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------

def summarise_weekly_counts(records: Iterable[JobRecord]) -> Dict[str, int]:
    buckets: Counter[str] = Counter()
    for record in records:
        week_key = week_floor(record.listing_date).date().isoformat()
        buckets[week_key] += 1
    return dict(sorted(buckets.items()))


def compute_skill_frequencies(records: Iterable[JobRecord]) -> Dict[str, int]:
    counts: Counter[str] = Counter()
    for record in records:
        if not record.description_text:
            continue
        for skill in extract_skills(record.description_text):
            counts[skill] += 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def collect_and_analyse(keywords: List[str]) -> Dict[str, dict]:
    session, cookies = build_session()
    summary: Dict[str, dict] = {}

    for keyword in keywords:
        print(f"Fetching listings for keyword: {keyword!r}")
        job_records = fetch_jobs_for_keyword(session, cookies, keyword)
        print(f"  collected {len(job_records)} recent postings")

        dataset_path = Path("data") / f"seek_{keyword.replace(' ', '_')}_jobs.json"
        dataset_path.write_text(
            json.dumps(
                [
                    {
                        "job_id": rec.job_id,
                        "title": rec.title,
                        "listing_date": rec.listing_date.isoformat(),
                        "location": rec.location,
                        "employer": rec.employer,
                        "work_type": rec.work_type,
                    }
                    for rec in job_records
                ],
                indent=2,
            )
        )

        weekly = summarise_weekly_counts(job_records)

        analysis_entry = {
            "keyword": keyword,
            "total_postings": len(job_records),
            "weekly_counts": weekly,
        }

        # Enrich AI-focused query with skill extraction.
        if COLLECT_SKILLS and "ai" in keyword.lower() and job_records:
            print("  loading job descriptions for skill analysis (AI roles)...")
            skills_counts: Counter[str] = Counter()
            for rec in job_records:
                detail_path = DETAIL_CACHE_DIR / f"{rec.job_id}.md"
                if detail_path.exists():
                    rec.description_text = detail_path.read_text()
                else:
                    markdown = fetch_job_markdown(rec.job_id)
                    if markdown:
                        rec.description_text = markdown
                        detail_path.write_text(markdown)
                    time.sleep(0.2)
                if rec.description_text:
                    for skill in extract_skills(rec.description_text):
                        skills_counts[skill] += 1

            skills = dict(sorted(skills_counts.items(), key=lambda item: (-item[1], item[0])))
            (Path("data") / "seek_ai_skills.json").write_text(json.dumps(skills, indent=2))
            analysis_entry["skill_frequencies"] = skills

        summary[keyword] = analysis_entry

    summary_path = Path("data") / "seek_job_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    return summary


def main() -> None:
    keywords = ["ai engineer", "python engineer"]
    summary = collect_and_analyse(keywords)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
