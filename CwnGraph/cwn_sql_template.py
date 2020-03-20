
cwn_sql_relations_templ = """
SELECT cwn_id, lemma_id, ref_id, {1} FROM {0} LEFT JOIN cwn_lemma
ON {0}.{1} == cwn_lemma.lemma_type
"""

cwn_sql_other_relations = """
SELECT lid, sense_id, facet_id, word, cwn_lemma.lemma_id AS rel_lemma_id, ref_id, rt FROM
(
SELECT lemma_id AS lid, sense_id, facet_id, word, ref_id, "hypo" AS rt FROM 上位詞 UNION
SELECT lemma_id AS lid, sense_id, facet_id, word, ref_id, "anto" AS rt FROM 反義詞 UNION
SELECT lemma_id AS lid, sense_id, facet_id, word, ref_id, "syno" AS rt FROM 同義詞 UNION
SELECT lemma_id AS lid, sense_id, facet_id, word, ref_id, "var" AS rt FROM 異體詞
) 
LEFT JOIN cwn_lemma ON word = cwn_lemma.lemma_type
"""

cwn_sql_cwn_relation_templ = """
SELECT cwn_id, rel_cwnid, cwn_symbol.label_en 
FROM cwn_relation LEFT JOIN cwn_symbol 
ON cwn_symbol.cwn_symbol = cwn_relation.rel_type
"""
