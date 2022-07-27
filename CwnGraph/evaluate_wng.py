import re
from typing import List, Tuple, Optional, Union, Dict
from wngual import parser
from wngual.ast_types import *  #type: ignore
from .cwn_types import CwnSense, CwnRelation

def evaluate_wngual(cgu, wng_str):
    ast = parser.parse(wng_str)
    res = None
    if isinstance(ast, wngComplexExpr):
        res = eval_complex_expr(cgu, ast)
    elif isinstance(ast, wngExpr):
        res = eval_expr(cgu, ast)
    return res

def eval_genitive_expr(cgu, ast:wngGenitiveExpr):
    if isinstance(ast.expr, wngSenseExpr):
        senses = eval_complex_expr(cgu, ast.expr)
    else:
        raise NotImplementedError("Does not support wngRelationExpr in wngGenitiveExpr")

    attr_name = ast.rel_spec.relation
    attr_args = ast.rel_spec.params
    attr_values = {}
    for sense_x in senses:
        attr_value = getattr(sense_x, attr_name)
        if callable(attr_value):
            attr_value = attr_value()
        attr_values[sense_x] = attr_value
    return attr_values

def eval_complex_expr(cgu, ast: wngComplexExpr):
    return eval_expr(cgu, ast.expr1)

def eval_expr(cgu, ast: wngExpr) -> Union[List[CwnSense], List[CwnRelation]]:
    if isinstance(ast, wngSenseExpr):
        return eval_sense_expr(cgu, ast)
    elif isinstance(ast, wngRelationExpr):
        return eval_relation_expr(cgu, ast)
    return []

def eval_sense_expr(cgu, sense_expr: wngSenseExpr) -> List[CwnSense]:
    pos = ""
    definition = ""
    for clause_x in sense_expr.clauses:    
        if isinstance(clause_x, wngSenseClause):
            con = clause_x.constraint
            if re.match("[A-Z][a-z0-9]{,2}", con):
                pos = con
            else:
                definition = con    
    if sense_expr.lemma:
        lemma = "^" + sense_expr.lemma + "$"
    else:
        lemma = sense_expr.lemma

    senses = cgu.find_senses(lemma, 
            pos=pos, 
            definition=definition)

    rel_clauses = [x for x in sense_expr.clauses
                   if isinstance(x, wngSenseRelClause)]
    senses = filter_sense_rel_clause(cgu, senses, rel_clauses)

    return senses

def filter_sense_rel_clause(cgu, senses, clauses: List[wngSenseRelClause]):
    for clause_x in clauses:        
        if isinstance(clause_x.tgt_values, wngSenseExpr):
            tgt_values = eval_sense_expr(cgu, clause_x.tgt_values)
        else:
            tgt_values = clause_x.tgt_values
        rel_spec = clause_x.rel_spec
        rel_op = clause_x.rel_op
        
        senses_pool = senses[::1]            
        for sense_x in senses_pool:
            if not satisfy_spec_sense(sense_x, rel_spec, rel_op, tgt_values):
                senses.remove(sense_x)
    
    return senses

def eval_relation_expr(cgu, relation_expr: wngRelationExpr) -> List[CwnRelation]:
    rel_spec = relation_expr.rel_spec
    arrow = relation_expr.arrow
    src_senses = eval_sense_expr(cgu, relation_expr.src)
    tgt_senses = eval_sense_expr(cgu, relation_expr.tgt)

    src_ids = set(x.id for x in src_senses)

    relations = []

    if arrow == ArrowType.forward:
        relations = [CwnRelation(cgu.edge_tgt_index.get(tgt_x.id), cgu)
                     for tgt_x in tgt_senses]
        relations = [x for x in relations 
                     if x.id[0] in src_ids and \
                        rel_spec and x.edge_type==rel_spec.relation]    

    elif arrow == ArrowType.bidirectional:
        relations_fwd = [CwnRelation(cgu.edge_tgt_index.get(tgt_x.id), cgu)
                     for tgt_x in tgt_senses]
        relations_bck = [CwnRelation(cgu.edge_src_index.get(tgt_x.id), cgu, reversed=True)
                     for tgt_x in tgt_senses]
        
        relations_fwd = [x for x in relations_fwd 
                         if x.id[0] in src_ids and \
                         rel_spec and x.edge_type==rel_spec.relation]

        relations_bck = [x for x in relations_bck
                         if x.id[1] in src_ids and \
                         rel_spec and x.edge_type==rel_spec.relation]

        relations = list(set(relations_fwd+relations_bck))

    else:
        raise NotImplementedError("backward arrow not implemeneted")

    return relations
        

def satisfy_spec_sense(sense: CwnSense, rel_spec: wngRelationSpec,
                rel_op: wngRelationOp, tgt_values: Union[str,List[CwnSense]]):
    attr_name = rel_spec.relation
    attr_args = rel_spec.params
    attr_value = getattr(sense, attr_name)
    if callable(attr_value):
        attr_value = attr_value()
        
    if not rel_op.negation:
        if rel_op.equality:
            return attr_value == tgt_values
        else:            
            return any(x in tgt_values for x in attr_value)
    
    else:
        if rel_op.equality:
            return attr_value != tgt_values
        else:
            return all(x not in tgt_values for x in attr_value)

    


