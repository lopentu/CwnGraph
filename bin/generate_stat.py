import json
from CwnGraph import CwnImage

if __name__ == "__main__":
    cwn = CwnImage.latest()
    with open("../stat.json", "w", encoding="UTF-8") as fout:
        meta = cwn.meta
        stat = cwn.statistics()
        json.dump({"meta": meta, "stat": stat}, fout, 
                    ensure_ascii=False, indent=2)
