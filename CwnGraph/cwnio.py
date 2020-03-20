import os
import json

def dump_json(V, E, prefix):
    with open(f"{prefix}_nodes.json", "w", encoding="UTF-8") as fout:
        json.dump(V, fout, indent=2, ensure_ascii=False)
    
    with open(f"{prefix}_edges.json", "w", encoding="UTF-8") as fout:        
        strE = {f"{k[0]}-{k[1]}": v for k, v in E.items()}
        json.dump(strE, fout, indent=2, ensure_ascii=False)

def dump_annot_json(meta, V, E, fpath):
    with open(fpath, "w", encoding="UTF-8") as fout:        
        strE = {f"{k[0]}-{k[1]}": v for k, v in E.items()}
        json.dump({"meta": meta, "V": V, "E": strE}, 
            fout, indent=2, ensure_ascii=False)

def load_annot_json(fpath):
    if not os.path.exists(fpath):
        raise FileNotFoundError(f"not found {fpath}")
    
    with open(fpath, "r", encoding="UTF-8") as fin:
        data = json.load(fin)
    
    V = data["V"]
    strE = data["E"]
    meta = data["meta"]
    E = {}

    for idstr, edata in strE.items():
        eid = tuple(idstr.split("-"))
        E[eid] = edata    
    return (meta, V, E)

def ensure_dir(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
        