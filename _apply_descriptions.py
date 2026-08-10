# -*- coding: utf-8 -*-
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
RAW = BASE / "data" / "raw" / "destinations_riau.json"
MAP = BASE / "_descriptions.json"

with MAP.open("r", encoding="utf-8") as f:
    descs = json.load(f)

with RAW.open("r", encoding="utf-8") as f:
    data = json.load(f)

updated = 0
for row in data:
    d = descs.get(row["id"])
    if d is not None and row.get("description") != d:
        row["description"] = d
        updated += 1

with RAW.open("w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"Updated {updated} of {len(data)} destinations.")
