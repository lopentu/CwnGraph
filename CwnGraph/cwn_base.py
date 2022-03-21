import pickle
from shutil import copyfile
from pathlib import Path
from .download import (
    get_manifest, get_cache_dir,
    ensure_image)
from .cwn_graph_utils import CwnGraphUtils
from . import cwn_stat
from . import cwnio

def load_cwn_image(fpath):
    with open(fpath, "rb") as fin:
        data = pickle.load(fin)
        if len(data) == 2:
            V, E = data
            meta = {}
        else:
            V, E, meta = data
    return V, E, meta

class CwnImage(CwnGraphUtils):
    def __init__(self, V, E, meta):
        super(CwnImage, self).__init__(V, E, meta)

    def __repr__(self):
        return "<CwnImage: {}>".format(self.meta.get("label", "<cwn-image>"))    

    @classmethod
    def load(cls, img_path_or_tag:str):
        # FIX THIS: CwnImage.load() is unnecessarily coupled with manifest
        manifest = get_manifest()
        tags = [x["tag"] for x in manifest["images"]]

        if not tags:
            raise ValueError("Something is wrong. There is no image in the manifest.")

        if img_path_or_tag == "latest":
            img_path_or_tag = tags[0]
        
        if img_path_or_tag in tags:
            image_path = ensure_image(img_path_or_tag)            
        else:
            image_path = img_path_or_tag

        V, E, meta = load_cwn_image(image_path)
        inst = CwnImage(V, E, meta)
        return inst

    @classmethod
    def latest(cls):
        return cls.load("latest")
    
    def save(self, fpath):
        with open(fpath, "wb") as fout:
            pickle.dump((self.V, self.E, self.meta), fout)
        return fpath

    def statistics(self):
        return cwn_stat.simple_statistics(self)
        
class CwnBase(CwnImage):
    """The base cwn reference data.
    """
    def __init__(self):
        manifest = get_manifest()
        image_path = ensure_image("base")
        V, E, meta = load_cwn_image(image_path)
        super(CwnBase, self).__init__(V, E, meta)            

    def __repr__(self):
        return "<CwnBase base-image>"