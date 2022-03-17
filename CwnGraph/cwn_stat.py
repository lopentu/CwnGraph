from CwnGraph.cwn_graph_utils import CwnGraphUtils
from CwnGraph.cwn_types.cwn_relation_types import CwnRelationType
from .cwn_types import CwnSense
try:
    from tqdm.auto import tqdm
except ImportError:
    tqdm = lambda x: x
    
def simple_statistics(cgu: CwnGraphUtils):
    n_lemma = 0
    n_sense = 0
    n_examples = 0
    n_sem_relations = 0


    for nid, ndata in tqdm(cgu.V.items()):
        if ndata["node_type"] == "lemma":
            n_lemma += 1
        elif ndata["node_type"] == "sense":
            n_sense += 1
            n_examples += len(CwnSense(nid, cgu).all_examples())

    for eid, edata in tqdm(cgu.E.items()):
        try:
            rel_type = CwnRelationType[edata['edge_type']]         
            if rel_type.is_semantic_relation():
                n_sem_relations += 1
        except KeyError:
            continue
    
    print("Statistics")
    print("------------")
    print("Number of lemma: ", n_lemma)
    print("Number of senses: ", n_sense)
    print("Number of examples: ", n_examples)
    print("Number of semantic relations: ", n_sem_relations)