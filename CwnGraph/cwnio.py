import os
import json

def dump_json(V, E, meta, prefix):
    with open(f"{prefix}_meta.json", "w", encoding="UTF-8") as fout:
        json.dump(meta, fout, indent=2, ensure_ascii=False)

    with open(f"{prefix}_nodes.json", "w", encoding="UTF-8") as fout:
        json.dump(V, fout, indent=2, ensure_ascii=False)
    
    with open(f"{prefix}_edges.json", "w", encoding="UTF-8") as fout:        
        strE = {f"{k[0]}-{k[1]}": v for k, v in E.items()}
        json.dump(strE, fout, indent=2, ensure_ascii=False)

def ensure_dir(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
        