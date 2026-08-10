# -*- coding: utf-8 -*-
"""Add latitude/longitude to each Riau destination (coordinate estimates)."""
import json
from pathlib import Path

RAW = Path(__file__).resolve().parent / "data" / "raw" / "destinations_riau.json"

COORDS = {
    "riau-001": [1.9438, 101.6260],
    "riau-002": [1.9880, 101.5510],
    "riau-003": [1.9750, 101.5600],
    "riau-004": [1.4930, 102.0800],
    "riau-005": [1.7900, 101.7300],
    "riau-006": [1.8000, 101.7200],
    "riau-007": [0.9800, 102.0400],
    "riau-008": [-0.3180, 103.1500],
    "riau-009": [-0.3720, 102.5510],
    "riau-010": [-0.7200, 102.2700],
    "riau-011": [0.1600, 101.1500],
    "riau-012": [0.4200, 101.1000],
    "riau-013": [0.3500, 101.0200],
    "riau-014": [0.3100, 101.0500],
    "riau-015": [1.2400, 102.9000],
    "riau-016": [1.1300, 102.8400],
    "riau-017": [1.2000, 102.7500],
    "riau-018": [1.1000, 102.7000],
    "riau-019": [1.2500, 102.7800],
    "riau-020": [1.0670, 102.6830],
    "riau-021": [-0.5450, 101.5100],
    "riau-022": [-0.6300, 101.5600],
    "riau-023": [-0.6000, 101.6000],
    "riau-024": [-0.5200, 101.4700],
    "riau-025": [-0.1500, 102.0000],
    "riau-026": [0.3500, 102.0500],
    "riau-027": [0.0300, 102.8300],
    "riau-028": [0.0300, 101.9000],
    "riau-029": [1.9500, 100.5500],
    "riau-030": [2.1200, 100.6200],
    "riau-031": [2.1680, 100.5870],
    "riau-032": [1.8500, 100.6500],
    "riau-033": [0.8500, 100.3300],
    "riau-034": [0.7000, 100.3500],
    "riau-035": [0.9000, 100.3000],
    "riau-036": [0.6500, 100.4500],
    "riau-037": [0.7830, 102.0450],
    "riau-038": [0.9000, 102.1500],
    "riau-039": [0.8800, 102.1300],
    "riau-040": [0.9800, 102.1500],
    "riau-041": [1.6670, 101.4470],
    "riau-042": [0.5200, 101.4500],
    "riau-043": [0.5160, 101.4450],
    "riau-044": [0.5500, 101.4500],
    "riau-045": [0.5050, 101.4400],
    "riau-046": [0.4700, 101.4300],
    "riau-047": [0.4800, 101.4200],
    "riau-048": [0.5100, 101.4430],
    "riau-049": [0.5550, 101.4700],
    "riau-050": [0.5110, 101.4410],
    "riau-051": [0.5300, 101.4550],
}


def main() -> None:
    with RAW.open("r", encoding="utf-8") as f:
        data = json.load(f)

    added = 0
    for row in data:
        coord = COORDS.get(row["id"])
        if coord is not None:
            row["latitude"] = coord[0]
            row["longitude"] = coord[1]
            added += 1

    with RAW.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Added coordinates to {added} of {len(data)} destinations.")


if __name__ == "__main__":
    main()
