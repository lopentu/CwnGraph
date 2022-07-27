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

def eval_complex_expr(cgu, ast: wngComplexExpr):
    return eval_expr(cgu, ast.expr1)

def eval_expr(cgu, ast: wngExpr) -> Union[List[CwnSense], List[CwnRelation]]:
    if isinstance(ast, wngSenseExpr):
        return eval_sense_expr(cgu, ast)
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

    for clause_x in sense_expr.clauses:
        if isinstance(clause_x, wngSenseRelClause):            
            if isinstance(clause_x.tgt_values, wngSenseExpr):
                tgt_values = eval_sense_expr(cgu, clause_x.tgt_values)
            else:
                tgt_values = clause_x.tgt_values
            rel_spec = clause_x.rel_spec
            rel_op = clause_x.rel_op
            
            senses_pool = senses[::1]            
            for sense_x in senses_pool:
                if not satisfy_spec(sense_x, rel_spec, rel_op, tgt_values):
                    senses.remove(sense_x)
    return senses

def satisfy_spec(sense: CwnSense, rel_spec: wngRelationSpec,
                rel_op: wngRelationOp, tgt_values: Union[str,List[CwnSense]]):
    attr_name = rel_spec.relation
    attr_args = rel_spec.params
    attr_value = getattr(sense, attr_name)
    if callable(attr_value):
        attr_value = attr_value()
    
    print(tgt_values, attr_value)
    if not rel_op.negation:
        if rel_op.equality:
            return attr_value == tgt_values
        else:            
            return all(x in tgt_values for x in attr_value)
    
    else:
        if rel_op.equality:
            return attr_value != tgt_values
        else:
            return all(x not in tgt_values for x in attr_value)

    


