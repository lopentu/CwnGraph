
import pickle
from . import cwn_graph_utils
import networkx as nx

with open("cwn_graph.pyobj", "rb") as fin:
    V, E = pickle.load(fin)
cgu = cwn_graph_utils.CwnGraphUtils(V, E)

G = nx.Graph()
for v in V.keys():
    G.add_node(v)
for e in E.keys():
    G.add_edge(e[0], e[1])

print("Available objects: ")
print("G: NetworkX graph object")
print("V: Raw vertices dictionary")
print("E: Raw edge dictionary")
print("cgu: CwnGraphUtils")
