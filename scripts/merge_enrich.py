#!/usr/bin/env python3
"""Merge enrichment JSON files into faculty.json, promoting matched records to 'fine'."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
RAW = DATA / "raw"

FILES = ["enrich_astro.json", "enrich_physics.json", "enrich_ese.json", "enrich_eng.json"]

FIELDS = ["title", "research_directions", "focus_areas", "summary",
          "email", "homepage", "publications"]


def norm_sources(s):
    if not s:
        return []
    if isinstance(s, str):
        return [s]
    return list(s)


def main():
    fac = json.loads((DATA / "faculty.json").read_text(encoding="utf-8"))
    by_id = {p["id"]: p for p in fac["professors"]}

    merged = 0
    for fn in FILES:
        fp = RAW / fn
        if not fp.exists():
            print(f"skip missing {fn}")
            continue
        recs = json.loads(fp.read_text(encoding="utf-8-sig"))
        for r in recs:
            pid = r.get("id")
            if pid not in by_id:
                continue
            p = by_id[pid]
            for k in FIELDS:
                if r.get(k):
                    p[k] = r[k]
            src = norm_sources(r.get("sources"))
            if src:
                existing = p.get("sources", [])
                for s in src:
                    if s not in existing:
                        existing.append(s)
                p["sources"] = existing
            # confidence rules: 'fine' if we have a summary + research_directions
            if p.get("summary") and p.get("research_directions"):
                p["confidence"] = "fine"
                p["verified"] = True
            elif p.get("summary"):
                p["confidence"] = "fine"
            merged += 1

    fac["generated_at"] = "2026-10-01T00:00:00Z"
    (DATA / "faculty.json").write_text(
        json.dumps(fac, ensure_ascii=False, indent=1), encoding="utf-8")

    from collections import Counter
    c = Counter(p["confidence"] for p in fac["professors"])
    print(f"merged {merged} enrichments; total {len(fac['professors'])}")
    print("confidence:", dict(c))
    print("with summary:", sum(1 for p in fac["professors"] if p.get("summary")))


if __name__ == "__main__":
    main()
