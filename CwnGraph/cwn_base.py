import pickle
from shutil import copyfile
from pathlib import Path
from .download import (
    get_manifest, get_cache_dir,
    ensure_image)
from .cwn_graph_utils import CwnGraphUtils
from . import cwn_stat
from . import cwnio
from .cwn_types import CwnSense, CwnSynset

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
    
    @classmethod
    def beta(cls):
        return cls.load("beta")
        
    def save(self, fpath):
        with open(fpath, "wb") as fout:
            pickle.dump((self.V, self.E, self.meta), fout)
        return fpath

    def statistics(self):
        return cwn_stat.simple_statistics(self)
    
    def to_graphviz(self, highlight=None, force_large=False):
        drawn_nodes = [nid 
            for nid, ndata in self.V.items() if
            ndata.get("node_type") != "lemma"]

        if len(drawn_nodes) > 80 and not force_large:
            raise ValueError(f"The image contains too many nodes ({len(drawn_nodes)}>50). " 
                             "The resulting graph will be too complicated. "
                             "Set `force_large=True` to override")
        
        import graphviz
        f = graphviz.Graph('subgraph', engine="neato")        
        f.attr('node', margin="0.01", height="0.1", width="0.1")
        undirected_edges = set()
        for nid, ndata in self.V.items():
            ntype = ndata.get("node_type")
            if ntype=="lemma": continue

            color = {"sense": "gray", 
                     "synset": "blue"}.get(ntype, "red")

            if ntype == "sense":
                sense = CwnSense(nid, self)
                node_tooltip = str(sense)
                node_label = sense.head_word
                node_shape = "rect"
            elif ntype == "synset":
                synset = CwnSynset(nid, self)
                node_tooltip = str(synset)
                node_label = ""
                node_shape = "point"
            else:
                node_label = nid
                node_tooltip = nid
                node_shape = "point"
            
            if highlight and nid == highlight:
                penwidth = "2"
            else:
                penwidth = "None"

            f.node(nid, label=node_label, shape=node_shape, 
                color=color, penwidth=penwidth,
                tooltip=node_tooltip)

        for eid, edata in self.E.items():    
            node_types = [self.V[x].get("node_type") for x in eid]
            if "lemma" in node_types:
                continue
            eid = tuple(sorted(eid))
            etype = edata.get("edge_type")
            if eid not in undirected_edges:
                color = {"hypernym": "red", "hyponym": "red", 
                         "holonym": "green", "meronym": "green",
                         "synonym": "blue", "is_synset": "deepskyblue", 
                         "has_synset": "blue"}.get(etype)
                f.edge(*eid, color=color, tooltip=etype)
                undirected_edges.add(eid)
        
        return f

        
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