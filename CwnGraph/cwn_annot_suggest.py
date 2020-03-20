from .cwn_annotator import CwnAnnotator
from .cwn_types import *
from typing import List, Dict, Tuple, Union
from .cwn_graph_utils import CwnGraphUtils

class CwnSuggestionAnnotator(CwnAnnotator):
    def __init__(self, cgu: CwnGraphUtils, suggestions: List[SuggestionData]):
        super(CwnSuggestionAnnotator, self).__init__(cgu, "auto_sug")
        self.suggestions = suggestions

    def annotate(self):
        # MISSING_SYNSET = auto()
        # (mem_x.id, dom_synset.id, CwnRelationType.is_synset)

        # NO_SYNSET = auto()
        # self.suggests(csg.NO_SYNSET, mem_x.id)

        # SYN_NO_SENSE = auto()
        # self.suggests(csg.SYN_NO_SENSE, synset_x.id)

        # SYN_WRONG_DEF = auto()
        # self.suggests(csg.SYN_WRONG_DEF, (mem_x.id, synset_x.definition))

        # SYN_MISSING_REL = auto()
        # self.suggests(csg.SYN_MISSING_REL, 
        #             (synset.id, rel_x[1], rel_x[0]))

        # SYN_REL_DIFF = auto()
        # self.suggests(csg.SYN_REL_DIFF, 
        #             (sense_y.id, rel_x[1], rel_x[0]))

        # INVERSE_ERROR = auto()
        # self.suggests(csg.INVERSE_ERROR, 
        #                 (rev_id[0], rev_id[1], rev_rel_type.name))

        # INVERSE_NOT_EXISTS = auto()
        # self.suggests(csg.INVERSE_NOT_EXISTS, 
        #                 (rev_id[0], rev_id[1], rev_rel_type.name))
        pass