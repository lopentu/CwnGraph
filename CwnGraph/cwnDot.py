
def get_node_color(ntype):
    if ntype == "glyph":
        return "red"
    elif ntype == "lemma":
        return "yellow"
    elif ntype == "sense":
        return "green"
    elif ntype == "facet":
        return "cyan"

def cwn_to_dot(fpath, V, E):    
    with open(fpath, "w", encoding="UTF-8") as fout:
        fout.write("graph{\n")
        fout.write("graph [bgcolor=\"#333333\"];\n")
        fout.write(
                "node [style=\"filled\", shape=\"point\"," + 
                "color=\"transparent\"];\n")
        nsub = set()
        for nid, ndata in V.items():
            # nsub.add(nid)
            # if len(nsub) > 1000: break

            fout.write("\"%s\" [label=\"\", fillcolor=\"%s\", node_type=\"%s\"];\n" % 
                    (nid, get_node_color(ndata["node_type"]), ndata["node_type"]))
        
        for eid in E.keys():
            # if eid[0] not in nsub or eid[1] not in nsub:
            #     continue
            fout.write("\"%s\" -- \"%s\";\n" % (eid[0], eid[1]))

        fout.write("}")


