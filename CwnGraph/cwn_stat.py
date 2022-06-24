from CwnGraph.cwn_graph_utils import CwnGraphUtils
from CwnGraph.cwn_types.cwn_relation_types import CwnRelationType
from .cwn_types import CwnSense, CwnLemma
try:
    from tqdm.auto import tqdm
except ImportError:
    tqdm = lambda x: x
    
def simple_statistics(cgu: CwnGraphUtils, include_all=True):
    n_lemma = 0
    n_sense = 0
    n_examples = 0
    n_synset = 0
    n_sem_relations = 0


    for nid, ndata in tqdm(cgu.V.items()):
        if ndata["node_type"] == "lemma":
            lemma = CwnLemma(nid, cgu)
            # only counts lemma with senses
            if include_all or lemma.senses:
                n_lemma += 1
        elif ndata["node_type"] == "sense":
            sense = CwnSense(nid, cgu)
            # only counts senses connected with lemma 
            # and having a definition
            if include_all or (sense.lemmas and sense.definition):
                n_sense += 1
                n_examples += len(sense.all_examples())
        elif ndata["node_type"] == "synset":
            n_synset += 1

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
    print("Number of synsets: ", n_synset)
    print("Number of examples: ", n_examples)
    print("Number of semantic relations: ", n_sem_relations)

    return {
        "n_lemma": n_lemma, "n_sense": n_sense,
        "n_synset": n_synset, "n_examples": n_examples, 
        "n_sem_relations": n_sem_relations
    }