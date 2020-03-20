import pickle
import hashlib
from enum import Enum, auto
from typing import Tuple
from collections import namedtuple

class AnnotAction(Enum):
    Edit = 1
    Delete = 2

class AnnotRecord:
    def __init__(self, annot_id:str, annot_action:AnnotAction, raw_id:str=None):
        self.action = annot_action
        self.annot_type = "generic"  
        self.annot_id = annot_id
        self.raw_id = raw_id

class GraphStructure:
    def __init__(self):
        self.V = {}
        self.E = {}
        self.meta = {}
        self._hash = None

    def compute_dict_hash(self, dict_obj):        
        m = hashlib.sha1()
        for k, value in sorted(dict_obj.items()):
            if isinstance(value, dict):
                m.update(pickle.dumps(k))                
                value_hash = self.compute_dict_hash(value)
                m.update(value_hash.encode())                 
            else:
                m.update(pickle.dumps((k, value)))                                       
        hash_value = m.hexdigest()
        return hash_value

    def get_hash(self):
        if not self._hash:
            Vhash = self.compute_dict_hash(self.V)
            Ehash = self.compute_dict_hash(self.E)
            m = hashlib.sha1()
            m.update(Vhash.encode())
            m.update(Ehash.encode())
            self._hash = m.hexdigest()        
        hashStr = self._hash[:6]
        return hashStr

    def export(self):
        print("export Graph ", self.get_hash())
        print("export to cwn_graph.pyobj, "
              "you may need to install it with CwnBase.install_cwn()")
        with open("data/cwn_graph.pyobj", "wb") as fout:
            pickle.dump((self.V, self.E), fout)

class CwnCheckerSuggestion(Enum):
    MISSING_SYNSET = auto()
    NO_SYNSET = auto()
    SYN_NO_SENSE = auto()
    SYN_WRONG_DEF = auto()
    SYN_MISSING_REL = auto()
    SYN_REL_DIFF = auto()
    INVERSE_ERROR = auto()
    INVERSE_NOT_EXISTS = auto()
csg = CwnCheckerSuggestion

SuggestionData = Tuple[CwnCheckerSuggestion, any]
class CwnIdNotFoundError(Exception):
    pass
