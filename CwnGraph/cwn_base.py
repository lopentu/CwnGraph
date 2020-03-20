import pickle
from shutil import copyfile
from pathlib import Path
from .cwn_graph_utils import CwnGraphUtils

class CwnBase(CwnGraphUtils):
    """The base cwn reference data.
    """

    def __init__(self):
        home_path = Path.home()                
        fpath = home_path / f".cwn_graph/cwn_graph.pyobj"
        if not fpath.exists():
            print("ERROR: install cwn_graph.pyobj first")
        with open(fpath, "rb") as fin:
            data = pickle.load(fin)
            if len(data) == 2:
                V, E = data
                meta = {}
            else:
                V, E, meta = data
        super(CwnBase, self).__init__(V, E, meta)        
    
    @staticmethod
    def install_cwn(cwn_path):
        """Install cwn for the first time.

        CwnGraph can be installed as a package. When running first time, 
        prepare ``cwn_graph.pyobj`` and install with :func:`install_cwn() <CwnGraph.cwn_base.CwnBase.install_cwn>`. 
        After installation, CwnGraph use CWN data in its own home directory, 
        regardless of working directory.
        
        Parameters
        ----------
        cwn_path : str
            Path to ``cwn_graph.pyobj``.
        """
        home_path = Path.home()
        cwn_user_dir = home_path / ".cwn_graph"
        if not cwn_user_dir.exists():
            cwn_user_dir.mkdir()
        try:        
            copyfile(cwn_path, cwn_user_dir / "cwn_graph.pyobj")
            print("CWN data installed")
        except FileNotFoundError as ex:
            print(ex)
            print("ERROR: install failed")