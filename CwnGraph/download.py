from pathlib import Path
import requests
import shutil

MANIFEST_URL = "https://raw.githubusercontent.com/lopentu/CwnGraph/develop/etc/manifest.json"

def get_cache_dir():
    cache_dir = Path("~/.cwn_graph").expanduser()
    cache_dir.mkdir(exist_ok=True, parents=True)
    return cache_dir

def update_manifest():
    import json
    print("updating manifest...")    
    manifest = requests.get(MANIFEST_URL).json()
    cache_dir = get_cache_dir()
    manifest_path = (cache_dir/"manifest.json")
    with manifest_path.open("w", encoding="UTF-8") as fout:
        json.dump(manifest, fout)
    print("manifest version: ", manifest.get("version", "<base>"))

def get_manifest():
    import json
    cache_dir = get_cache_dir()
    manifest_path = (cache_dir/"manifest.json")
    if not manifest_path.exists():
        update_manifest()
    with manifest_path.open("r", encoding="UTF-8") as fin:
        manifest = json.load(fin)
    return manifest

def list_images():
    manifest = get_manifest()
    return [x["tag"] for x in manifest["images"]]

def download_image(google_drive_id: str):
    import gdown    
    down_file = gdown.download(id=google_drive_id, quiet=False)
    cache_dir = get_cache_dir()
    model_path = cache_dir / down_file
    shutil.move(down_file, model_path)
    print("image has downloaded: ", down_file)

def ensure_image(tag: str):
    manifest = get_manifest()
    img_info = [x for x in manifest["images"] if x["tag"] == tag]
    
    if not img_info:
        raise ValueError(f"tag {tag} not found")
    else:
        img_info = img_info[0]
        if "note" in img_info:
            print("[NOTE]", img_info["note"])
        img_cache_path = get_cache_dir() / img_info["file"]
        if not img_cache_path.exists():
            print(f"downloading image: {img_info['drive_id']}...")
            download_image(img_info["drive_id"])
        return img_cache_path        

def download():
    print("Deprecation note: download() is no longer needed after 0.3.0.")
    print("    Data would be downloaded automatically when calling CwnGraph.CwnBase().")


    