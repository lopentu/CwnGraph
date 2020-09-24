import os
import zipfile
import tempfile

def get_model_path():
    home_dir = os.path.expanduser("~")
    cache_dir = os.path.join(home_dir, ".cwn_graph")
    model_path = os.path.join(cache_dir, "cwn_graph.pyobj")
    return model_path

def download(upgrade=False):
    if os.path.exists(get_model_path()) and not upgrade:
        print("A copy of cwn_grpah.pyobj already exists. Use upgrade=True to overwrite")
        return 

    import gdown
    url = "https://drive.google.com/uc?id=1opGRw490cAizoj2JHzR8UIZME3Mc65Ze"    
    model_path = get_model_path()
    gdown.download(url, model_path, quiet=False)  
    print("CwnGraph data installed.")      


    