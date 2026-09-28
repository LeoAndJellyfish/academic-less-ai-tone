"""Count Han characters in a revision field and check an explicit interval."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re

def measure(text: str, lower: int, upper: int) -> dict:
    if lower < 0 or upper < lower:
        raise ValueError("Require 0 <= min <= max")
    count = len(re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff]", text))
    return {"han_count":count,"minimum":lower,"maximum":upper,
            "length_met":lower <= count <= upper,
            "short_by":max(0,lower-count),"over_by":max(0,count-upper),
            "counting_rule":"U+3400–4DBF、U+4E00–9FFF；仅revision正文"}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--min",type=int,required=True,dest="lower")
    p.add_argument("--max",type=int,required=True,dest="upper")
    args=p.parse_args()
    payload=json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(payload.get("revision"),str):
        raise ValueError("Input must contain a revision string")
    result=measure(payload["revision"],args.lower,args.upper)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if not result["length_met"]:
        raise SystemExit(2)

if __name__=="__main__":
    main()
