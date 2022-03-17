from .cwn_base import CwnBase, CwnImage
from .cwn_graph import CWN_Graph
from . import cwnio as io
from .cwn_graph_utils import CwnGraphUtils
from .cwn_types import *
from .download import update_manifest, list_images

#
# download manifest
# 
from pathlib import Path
cache_dir = Path("~/.cwn_graph").expanduser()
cache_dir.mkdir(exist_ok=True, parents=True)
manifest_path = cache_dir / "manifest.json"
if not manifest_path.exists():
    update_manifest()
