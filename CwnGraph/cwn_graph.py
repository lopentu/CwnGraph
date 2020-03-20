import sqlite3
import logging
import pdb
from .cwn_sql_template import *
from .cwn_types import CwnRelationType

class CWN_Graph:
    def __init__(self, dbconn):
        self.logger = logging.getLogger("CwnGraph.cwn_graph")
        self.logger.setLevel(logging.INFO)
        self.cur = dbconn.cursor()
        self.V = {}
        self.E = {}
        self.glyph = {}
        self.import_nodes()
        self.import_edges()
    
    def normalize_cwnid(self, cwnid):
        """why normalizing cwn_id??
        """
        if cwnid.startswith("syn") or \
           cwnid.startswith("pwn"):
           return cwnid

        if not cwnid:
            return cwnid

        if len(cwnid) >= 10:
            cwnid = cwnid[:10]
        else:
            pass
        
        return cwnid

    def import_nodes(self):
        self.import_node_cwn_glyph()
        self.import_node_cwn_lemma()
        self.import_node_cwn_sense()
        self.import_node_cwn_synset()
        self.import_node_cwn_pwnoffset()
        self.import_node_cwn_facet()
        
        print("V cardinality: %d " % (len(self.V),))

    def import_edges(self):
        self.import_edge_cwn_lemma()
        self.import_edge_cwn_sense()        
        self.import_edge_cwn_facet()
        self.import_edge_cwn_antonym()
        self.import_edge_cwn_holo()
        self.import_edge_cwn_hypo()
        self.import_edge_cwn_mero()
        self.import_edge_cwn_nearsyno()
        self.import_edge_cwn_synonym()
        self.import_edge_cwn_upword()
        self.import_edge_cwn_synset()
        self.import_edge_cwn_pwnoffset()
        self.import_edge_varword()
        self.import_edge_relations()
        self.import_edge_cwn_relation()
        print("E cardinality: %d " % (len(self.E),))
        return
    
    def import_node_cwn_glyph(self):
        print("importing glyph nodes")
        rows = self.select_query("SELECT lemma_type FROM cwn_lemma")
        counter = 0
        for r in rows:
            gtxt = r[0]
            if not r[0]:
                self.logger.info("empty lemma")
                continue

            if r[0][-1] in "0123456789":
                gtxt = r[0][:-1]
            
            if gtxt not in self.glyph:
                counter += 1
                node_data = {
                    "node_type": "glyph",
                    "glyph": gtxt
                }
                gid = "G" + str(counter)
                self.glyph[gtxt] = gid
                self.add_node(gid, node_data)
        
    def import_node_cwn_lemma(self):
        print("importing lemma nodes")
        rows = self.select_query("SELECT lemma_id, cwn_zhuyin, "
            "lemma_type, lemma_sno FROM cwn_lemma")
        for r in rows:        
            if r[0] is None or len(r[0]) == 0:
                self.logger.info("Skip lemma with no id: %s" % (r[1],))
                continue

            node_id = r[0]
            node_data = {
                "node_type": "lemma",
                "lemma_sno": r[3],
                "lemma": r[2],
                "zhuyin": r[1]
            }
            self.add_node(node_id, node_data)

    def import_node_cwn_sense(self):
        print("importing sense nodes")
        rows = self.select_query("""
        SELECT sense_id, sense_def, domain_id, 
        group_concat(pos), group_concat(cwn_example.example_cont, ";")
        FROM cwn_sense 
        LEFT JOIN cwn_pos ON cwn_sense.sense_id == cwn_pos.cwn_id 
        LEFT JOIN cwn_example ON cwn_sense.sense_id == cwn_example.cwn_id
        GROUP BY sense_id
        """
        )

        def pick_pos(poslist):
            unique_pos = list(set(poslist.split(",")))
            if len(unique_pos) == 1:
                return unique_pos[0]
            else:
                return ",".join(unique_pos)
                
        for r in rows:
            if r[0] is None or len(r[0]) == 0:
                continue
            node_id = r[0]
            node_data = {
                "node_type": "sense",
                "def": r[1],
                "domain": r[2] if r[2] is not None else "",
                "pos": pick_pos(r[3]) if r[3] is not None else "",
                "examples": [x.strip() for x in r[4].split(";")] if r[4] is not None else ""
                }
            self.add_node(node_id, node_data)

    def import_node_cwn_synset(self):
        print("importing synset nodes")

        rows = self.select_query("""
        SELECT id, gloss, member, pwn_word, pwn_id
        FROM cwn_goodsynset        
        """)

        for r in rows:
            node_id = f"syn_{r[0]:06d}"
            node_data = {
                "node_type": "synset",
                "gloss": r[1],                
                "pwn_word": r[3],
                "pwn_id": r[4]
            }
            self.add_node(node_id, node_data)

    def import_node_cwn_pwnoffset(self):
        print("importing PWN offsets")

        rows = self.select_query("""
        SELECT synset_sno, synset_word1, synset_offset 
        FROM cwn_synset
        """)

        for r in rows:
            if not r[2]: continue
            node_id = f"pwn_{r[2].strip()}"
            node_data = {
                "node_type": "pwn_synset",
                "synset_sno": r[0],
                "synset_word1": r[1]
            }
            self.add_node(node_id, node_data)

    def import_node_cwn_facet(self):
        print("importing facet nodes")
        rows = self.select_query(
                "SELECT facet_id, facet_def, domain_id, group_concat(pos), "
                "group_concat(cwn_example.example_cont, ';') "
                "FROM cwn_facet "
                "LEFT JOIN cwn_pos ON cwn_facet.facet_id == cwn_pos.cwn_id "
                "LEFT JOIN cwn_example ON cwn_facet.facet_id == cwn_example.cwn_id "                
                "GROUP BY facet_id")
            
        def pick_pos(poslist):
            unique_pos = list(set(poslist.split(",")))
            if len(unique_pos) == 1:
                return unique_pos[0]
            else:
                return ",".join(unique_pos)

        for r in rows:
            if r[0] is None or len(r[0]) == 0:
                continue
            node_id = r[0]
            node_data = {
                "node_type": "facet",
                "def": r[1],
                "domain": r[2] if r[2] is not None else "",
                "pos": pick_pos(r[3]) if r[3] is not None else "",
                "examples": [x.strip() for x in r[4].split(";")] if r[4] is not None else ""
                }
            self.add_node(node_id, node_data)
    
    def import_edge_cwn_lemma(self):
        print("importing lemma edges")
        rows = self.select_query(
                "SELECT lemma_type, lemma_id FROM cwn_lemma "
               )

        for r in rows:
            if not r[0]:
                self.logger.info("empty lemma")
                continue
            gtxt = r[0]            
            if r[0][-1] in "0123456789":
                gtxt = r[0][:-1]
            
            if gtxt in self.glyph:
                gid = self.glyph[gtxt]
                self.add_edge(gid, r[1], {"edge_type": "has_lemma"})        

    def import_edge_cwn_sense(self):
        print("importing sense edges")
        rows = self.select_query(
                "SELECT lemma_id, sense_id FROM cwn_sense "
               )
        for r in rows:
            self.add_edge(r[0], r[1], {"edge_type": "has_sense"})        

    def import_edge_cwn_synset(self):
        print("importing synset edges")
        rows = self.select_query(
                "SELECT id, member FROM cwn_goodsynset"
               )
        for r in rows:
            if not r[1]: continue
            members = r[1].split(",")            
            for m in members:
                synsetid =  f"syn_{r[0]:06d}"
                self.add_edge(m.strip(), synsetid, {"edge_type": "is_synset"})

    def import_edge_cwn_pwnoffset(self):
        print("importing PWN offset edges")
        rows = self.select_query(
                "SELECT cwn_id, synset_offset, synset_cwnrel FROM cwn_synset"
               )
        for r in rows:
            if not r[1]: continue
            rel_type = CwnRelationType.from_zhLabel(r[2]).name
            self.add_edge(r[0], f"pwn_{r[1].strip()}", {"edge_type": rel_type})

    def import_edge_cwn_facet(self):
        print("importing facet edges")
        rows = self.select_query(
                "SELECT sense_id, facet_id FROM cwn_facet "
               )
        for r in rows:
            self.add_edge(r[0], r[1], {"edge_type": "has_facet"})        

    def import_edge_cwn_antonym(self):
        print("importing antonym edges")
        rows = self.select_query(
               self.prepare_relation_sql(
                   "cwn_antonym", "antonym_word")
               )
        for r in rows:
            resolved_id = self.resolve_refid(r[1], r[2], r[3])            
            self.add_edge(r[0], resolved_id, {"edge_type": "antonym"})        
        
    def import_edge_cwn_synonym(self):
        print("importing synonym edges")
        rows = self.select_query(
               self.prepare_relation_sql(
                   "cwn_synonym", "synonym_word")
               )
        for r in rows:
            resolved_id = self.resolve_refid(r[1], r[2], r[3])            
            self.add_edge(r[0], resolved_id, {"edge_type": "synonym"})        
    
    def import_edge_cwn_holo(self):
        print("importing holonym edges")
        rows = self.select_query(
               self.prepare_relation_sql(
                   "cwn_holonym", "holo_word")
               )
        for r in rows:
            resolved_id = self.resolve_refid(r[1], r[2], r[3])            
            self.add_edge(r[0], resolved_id, {"edge_type": "holonym"})        

    def import_edge_cwn_hypo(self):
        print("importing hyponym edges")
        rows = self.select_query(
               self.prepare_relation_sql(
                   "cwn_hyponym", "hypo_word")
               )
        for r in rows:
            resolved_id = self.resolve_refid(r[1], r[2], r[3])            
            self.add_edge(r[0], resolved_id, {"edge_type": "hyponym"})        

    def import_edge_cwn_mero(self):
        print("importing meronym edges")
        rows = self.select_query(
               self.prepare_relation_sql(
                   "cwn_meronym", "mero_word")
               )
        for r in rows:
            resolved_id = self.resolve_refid(r[1], r[2], r[3])            
            self.add_edge(r[0], resolved_id, {"edge_type": "meronym"})        

    def import_edge_cwn_nearsyno(self):
        print("importing nearsynonym edges")
        rows = self.select_query(
               self.prepare_relation_sql(
                   "cwn_nearsynonym", "nearsyno_word")
               )
        for r in rows:
            resolved_id = self.resolve_refid(r[1], r[2], r[3])            
            self.add_edge(r[0], resolved_id, {"edge_type": "nearsynonym"})        
            
    def import_edge_cwn_upword(self):
        print("importing hypernym edges")
        rows = self.select_query(
               self.prepare_relation_sql(
                   "cwn_upword", "up_word")
               )
        for r in rows:
            resolved_id = self.resolve_refid(r[1], r[2], r[3])            
            self.add_edge(r[0], resolved_id, {"edge_type": "hypernym"})        

    def import_edge_varword(self):
        print("importing varwords edges")
        rows = self.select_query(
               self.prepare_relation_sql(
                   "cwn_variant", "var_word")
               )
        for r in rows:
            resolved_id = self.resolve_refid(r[1], r[2], r[3])            
            self.add_edge(r[0], resolved_id, {"edge_type": "varword"})        

    def import_edge_cwn_relation(self):
        print("importing varwords edges")
        rows = self.select_query(cwn_sql_cwn_relation_templ)
        for r in rows:
            from_id = r[0]
            to_id = r[1]
            rel_type = r[2]
            self.add_edge(from_id, to_id, {"edge_type": rel_type})
        
    def import_edge_relations(self):
        print("importing other relation edges")
        rows = self.select_query(cwn_sql_other_relations)
        for r in rows:
            resolved_id = self.resolve_refid(r[4], r[5], r[3])            
            from_cwn_id = r[0]+r[1]+r[2]
            self.add_edge(from_cwn_id, resolved_id, {"edge_type": "varword"})        

    def prepare_relation_sql(self, tbl, wfield):
        sql = cwn_sql_relations_templ.format(tbl, wfield)
        return sql
        

    def add_node(self, node_id, node_data):
        V = self.V
        if len(node_id) == 0: 
            self.logger.warning("Empty node id: %a" % (node_data, ))
            return

        if node_id not in V:
            V[node_id] = node_data
        else:
            self.logger.info("Duplicate node id: %s" % (node_id,))
    
    def add_edge(self, from_id, to_id, edge_data):
        V = self.V
        E = self.E
        if not from_id or not to_id: 
            return 

        from_id = self.normalize_cwnid(from_id)
        to_id = self.normalize_cwnid(to_id)
        if from_id not in V:
            self.logger.warning("from_node missing: "+
                    "%s - %s" % (from_id, to_id))
            return
        
        if to_id not in V:
            self.logger.warning("to_node missing: "+
                    "%s - %s" % (from_id, to_id))
            return
        
        if (from_id, to_id) not in E:
            E[(from_id, to_id)] = edge_data
        else:
            self.logger.info("Duplicate edge: %s - %s" % (from_id, to_id))


    def select_query(self, sqlcmd):
        return self.cur.execute(sqlcmd).fetchall()
    
    def resolve_lemma(self, lemma, lemma_sno):
        if lemma_sno:
            sql_command = f"""
            SELECT lemma_id FROM cwn_lemma
            WHERE lemma_type == "{lemma}" AND lemma_sno == {lemma_sno}
            """
        else:
            sql_command = f"""
            SELECT lemma_id FROM cwn_lemma
            WHERE lemma_type == "{lemma}"
            """
        
        rows = self.select_query(sql_command)
        if not rows:
            return None

        for r in rows:
            # just ignore the rest
            return r[0]
            

    def resolve_refid(self, lemma_id, ref_id, lemma):
        # if ref_id is None, lemma_id is in fact cwn_id        
        if ref_id is None:
            return lemma_id
        
        if lemma_id is None:
            if lemma[-1] in "0123456789":
                lemma_id = self.resolve_lemma(lemma[:-1], lemma[-1])
            else:
                lemma_id = self.resolve_lemma(lemma[:-1], None)

            if not lemma_id:
                self.logger.warning("Cannot find lemma %s" % (lemma,))
                return ""
            else:
                # recover successfully, continue
                pass

        if not ref_id:
            ref_id="0100"
        elif len(ref_id) != 4:              
            self.logger.warning("invalid ref_id format: %s,%s,%s", lemma_id, ref_id, lemma)
            return ""

        sense_part = ref_id[0:2]
        homo_part = ref_id[2]
        facet_part = ref_id[3]
        if facet_part == '0':
            return lemma_id + sense_part
        else:
            return lemma_id + sense_part + "0" + facet_part
