#!/usr/bin/env python3
"""Assemble coarse faculty.json for NJU physics-related schools.

Sources (data/raw/):
  - physics_by_dept.txt  物理学院 按系别
  - astro.txt            天文与空间科学学院
  - ese.txt              电子科学与工程学院
  - eng_api.json         现代工程与应用科学学院 (API payload)
"""
import json
import re
from pathlib import Path
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
RAW = DATA / "raw"

PHYS_SCHOOL = "南京大学 / Nanjing University"
PHYS_NAME = "南京大学"

# 物理学院 杰出人才 (院士 + 国家级人才 + 青年) -> mark academician / talent
PHYS_ACADEMICIANS = {
    "都有为", "龚昌德", "马余强", "王广厚", "邢定钰", "张淑仪", "祝世宁", "邹志刚",
}
# ESE + astro academicians
ESE_ACADEMICIANS = {"吴培亨", "郑有炓", "郑海荣", "施毅"}
ASTRO_ACADEMICIANS = {"方成", "曲钦岳", "苏定强", "孙义燧"}
ENG_ACADEMICIANS = {"祝世宁", "邹志刚", "陈延峰"}


def slug_pinyin(name):
    s = name.strip().lower()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^a-z0-9\u4e00-\u9fff-]", "", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "x"


def clean_name(n):
    return re.sub(r"\s+", "", n.strip())


def parse_tsv(path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        rows.append((parts[0].strip(), clean_name(parts[1]), parts[2].strip()))
    return rows


def main():
    profs = []
    seen_names_by_dept = set()

    def add(rec):
        key = (rec.get("department", ""), rec["name"])
        if key in seen_names_by_dept:
            return
        seen_names_by_dept.add(key)
        rec["id"] = f"nju-{slug_pinyin(rec['name'])}-{len(profs):04d}"
        profs.append(rec)

    # --- 物理学院 ---
    phys_dept_map = {
        "现代物理系": "物理学院-现代物理系",
        "物理学系": "物理学院-物理学系",
        "光电科学系": "物理学院-光电科学系",
        "声科学与工程系": "物理学院-声科学与工程系",
        "基础物理教学中心": "物理学院-基础物理教学中心",
        "院直属": "物理学院-院直属",
    }
    for dept, name, url in parse_tsv(RAW / "physics_by_dept.txt"):
        add({
            "name": name,
            "name_local": name,
            "school": PHYS_SCHOOL,
            "department": phys_dept_map.get(dept, f"物理学院-{dept}"),
            "subject": "物理学 / Physics",
            "title": "",
            "profile_url": url,
            "sources": ["http://physics.nju.edu.cn/szdw/qbmd/axb/index.html"],
            "confidence": "coarse",
            "verified": False,
            "is_academician": name in PHYS_ACADEMICIANS,
        })

    # --- 天文与空间科学学院 ---
    astro_title_map = {
        "中科院院士": "中国科学院院士",
        "教授": "教授",
        "副教授": "副教授",
        "助理教授": "助理教授",
        "专职科研": "专职科研",
    }
    for grp, name, url in parse_tsv(RAW / "astro.txt"):
        add({
            "name": name,
            "name_local": name,
            "school": PHYS_SCHOOL,
            "department": "天文与空间科学学院",
            "subject": "天文学 / Astronomy",
            "title": astro_title_map.get(grp, grp),
            "profile_url": url,
            "sources": ["https://astronomy.nju.edu.cn/szll/szgk/index.html"],
            "confidence": "coarse",
            "verified": False,
            "is_academician": name in ASTRO_ACADEMICIANS,
        })

    # --- 电子科学与工程学院 ---
    for cat, name, url in parse_tsv(RAW / "ese.txt"):
        add({
            "name": name,
            "name_local": name,
            "school": PHYS_SCHOOL,
            "department": "电子科学与工程学院",
            "subject": "电子科学与技术 / Electronics",
            "title": "",
            "profile_url": url,
            "sources": ["http://ese.nju.edu.cn/30444/list.htm"],
            "confidence": "coarse",
            "verified": False,
            "is_academician": name in ESE_ACADEMICIANS,
        })

    # --- 现代工程与应用科学学院 ---
    eng = json.loads((RAW / "eng_api.json").read_text(encoding="utf-8-sig"))
    # group field: department or exField1 fallback
    for rec in eng.get("data", []):
        name = clean_name(rec.get("title", ""))
        if not name:
            continue
        dept = rec.get("department", "") or rec.get("exField1", "") or "现代工程与应用科学学院"
        cat = rec.get("exField1", "") if isinstance(rec.get("exField1"), str) else ""
        add({
            "name": name,
            "name_local": name,
            "school": PHYS_SCHOOL,
            "department": f"现代工程与应用科学学院-{dept}" if dept != "现代工程与应用科学学院" else "现代工程与应用科学学院",
            "subject": "工程与应用科学 / Applied Science",
            "title": "",
            "profile_url": rec.get("cnUrl", ""),
            "sources": ["https://eng.nju.edu.cn/qyml2/list.htm"],
            "confidence": "coarse",
            "verified": False,
            "is_academician": name in ENG_ACADEMICIANS,
        })

    out = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "query": {
            "schools": [PHYS_SCHOOL],
            "departments": [
                "物理学院", "现代工程与应用科学学院",
                "电子科学与工程学院", "天文与空间科学学院",
            ],
            "topics": ["物理学相关 / Physics-related"],
        },
        "professors": profs,
    }
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "faculty.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"total professors: {len(profs)}")
    from collections import Counter
    for k, v in Counter(p["department"] for p in profs).most_common():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
