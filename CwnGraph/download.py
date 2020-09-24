import os
import zipfile
import tempfile

def download(upgrade=False):
    import gdown

    home_dir = os.path.expanduser("~")
    cache_dir = os.path.join(home_dir, ".cwn_graph")
    
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    model_path = os.path.join(cache_dir, "cwn_graph.pyobj")    
    
    if os.path.exists(model_path) and not upgrade:
        print("A copy of cwn_grpah.pyobj already exists. Use upgrade=True to overwrite")
        return 

    url = "https://drive.google.com/uc?id=1opGRw490cAizoj2JHzR8UIZME3Mc65Ze"        
        
    gdown.download(url, model_path, quiet=False)  
    print("CwnGraph data installed.")      


    