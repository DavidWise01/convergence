#!/usr/bin/env python3
"""Bounded, evidence-oriented harvester for public CERN records (stdlib only).

Default: metadata only. Optional downloads: publicly marked CC0 files under
strict size quotas. No authentication, credentials, bypass, or unrestricted crawl.
"""
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import time
import urllib.error
import urllib.parse
import urllib.request

BASES = {
    "open_data": "https://opendata.cern.ch/api/records/",
    "repository": "https://repository.cern/api/records",
}
UA = "Convergence-H015-CERN-Public-Research/1.0 (+https://github.com/DavidWise01/convergence)"
HEADERS = {"User-Agent": UA, "Accept": "application/json"}


def request_json(url, timeout=25):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        if resp.status != 200:
            raise RuntimeError("HTTP " + str(resp.status))
        return json.load(resp)


def record_list(payload):
    hits = payload.get("hits", {})
    if isinstance(hits, dict):
        return hits.get("hits", [])
    if isinstance(hits, list):
        return hits
    return []


def record_url(base, page, size, query):
    params = {"page": page, "size": size}
    if query:
        params["q"] = query
    return base + "?" + urllib.parse.urlencode(params)


def flatten_record(item, source, fetched_url, at):
    metadata = item.get("metadata", {})
    record_id = str(item.get("id", item.get("recid", "")))
    links = item.get("links", {})
    file_info = item.get("files", {})
    entries = file_info.get("entries", {}) if isinstance(file_info, dict) else {}
    if isinstance(entries, dict):
        files = [{"key": k, "size": v.get("size"), "checksum": v.get("checksum"),
                  "url": v.get("links", {}).get("content")}
                 for k, v in entries.items() if isinstance(v, dict)]
    elif isinstance(entries, list):
        files = [{"key": f.get("key"), "size": f.get("size"), "checksum": f.get("checksum"),
                  "url": f.get("links", {}).get("content")} for f in entries if isinstance(f, dict)]
    else:
        files = []
    title = metadata.get("title", item.get("title", ""))
    license_value = metadata.get("license", metadata.get("rights", ""))
    return {
        "source": source,
        "source_api_url": fetched_url,
        "retrieved_utc": at,
        "record_id": record_id,
        "title": title,
        "publication_date": metadata.get("publication_date") or metadata.get("date"),
        "doi": metadata.get("doi"),
        "license": license_value,
        "public_record_url": links.get("self_html") or links.get("self") or (
            "https://opendata.cern.ch/record/" + record_id if source == "open_data" else
            "https://repository.cern/records/" + record_id),
        "files": files,
    }


def is_cc0(value):
    if isinstance(value, dict):
        value = " ".join(str(x) for x in value.values())
    elif isinstance(value, list):
        value = " ".join(str(x) for x in value)
    return "cc0" in str(value).lower()


def allowed_url(url):
    if not isinstance(url, str):
        return False
    u = urllib.parse.urlparse(url)
    return u.scheme == "https" and u.hostname in {
        "opendata.cern.ch", "opendata.web.cern.ch", "repository.cern"
    }


def download_small_file(entry, dst, quota_bytes, max_file_bytes):
    size = entry.get("size")
    url = entry.get("url")
    if not allowed_url(url) or not isinstance(size, int) or size > max_file_bytes or size > quota_bytes:
        return None, quota_bytes
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    hasher = hashlib.sha256()
    parts = []
    n = 0
    with urllib.request.urlopen(req, timeout=30) as resp:
        # Guard redirects to unknown hosts.
        if not allowed_url(resp.geturl()):
            raise ValueError("Redirect outside explicitly permitted CERN hosts")
        while True:
            chunk = resp.read(min(65536, max_file_bytes - n + 1))
            if not chunk:
                break
            n += len(chunk)
            if n > max_file_bytes or n > quota_bytes:
                raise ValueError("Size quota exceeded while streaming")
            hasher.update(chunk)
            parts.append(chunk)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(b"".join(parts))
    return {"path": str(dst), "bytes": n, "sha256": hasher.hexdigest(), "source_url": url}, quota_bytes - n


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pages", type=int, default=2)
    p.add_argument("--size", type=int, default=10)
    p.add_argument("--max-records", type=int, default=40)
    p.add_argument("--query", default="")
    p.add_argument("--download-cc0", action="store_true")
    p.add_argument("--max-file-mb", type=int, default=2)
    p.add_argument("--max-total-mb", type=int, default=10)
    p.add_argument("--output", default="cern-public/harvest")
    a = p.parse_args()
    if not (1 <= a.pages <= 10 and 1 <= a.size <= 25 and 1 <= a.max_records <= 250
            and 1 <= a.max_file_mb <= 25 and 1 <= a.max_total_mb <= 100):
        p.error("Bounds: pages 1..10, size 1..25, records 1..250, file MB 1..25, total MB 1..100")
    out = pathlib.Path(a.output)
    out.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    seen, records, errors, hashes = set(), [], [], []
    quota = a.max_total_mb * 1048576
    for source, base in BASES.items():
        for page in range(1, a.pages + 1):
            if len(records) >= a.max_records:
                break
            url = record_url(base, page, a.size, a.query)
            try:
                payload = request_json(url)
                items = record_list(payload)
            except (urllib.error.URLError, OSError, ValueError, RuntimeError) as exc:
                errors.append({"source": source, "request_url": url, "error": str(exc)})
                break
            if not items:
                break
            for item in items:
                if len(records) >= a.max_records:
                    break
                rec = flatten_record(item, source, url, now)
                key = (source, rec["record_id"])
                if key in seen:
                    continue
                seen.add(key)
                records.append(rec)
                if a.download_cc0 and source == "open_data" and is_cc0(rec["license"]):
                    for idx, file_entry in enumerate(rec["files"]):
                        safe_id = "".join(c for c in rec["record_id"] if c.isalnum() or c in "-_")
                        name = str(file_entry.get("key", "item")).split("/")[-1]
                        safe_name = "".join(c for c in name if c.isalnum() or c in "-_.")[:90] or str(idx)
                        try:
                            h, quota = download_small_file(
                                file_entry, out / "downloads" / safe_id / safe_name,
                                quota, a.max_file_mb * 1048576)
                            if h:
                                hashes.append(h)
                        except (urllib.error.URLError, OSError, ValueError) as exc:
                            errors.append({"record": rec["record_id"],
                                           "file": file_entry.get("key"), "error": str(exc)})
            time.sleep(0.25)
    with (out / "records.jsonl").open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
    (out / "errors.json").write_text(json.dumps(errors, indent=2) + "\n", encoding="utf-8")
    (out / "sha256.json").write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "schema": "convergence.h015.public-metadata.v1",
        "retrieved_utc": now, "records": len(records), "errors": len(errors),
        "downloaded_files": len(hashes), "public_only": True, "sources": BASES,
        "query": a.query, "metadata_only": not a.download_cc0,
        "limitations": "Bounded sample of public search results; not a complete CERN archive."
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0 if records else 2


if __name__ == "__main__":
    raise SystemExit(main())
