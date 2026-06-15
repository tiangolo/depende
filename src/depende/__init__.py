from .main import Depends as Depends
from .main import DependsInfo as DependsInfo
from .main import detect_cycles as detect_cycles
from .main import get_dependency_graph as get_dependency_graph
from .main import solve_dependencies as solve_dependencies

try:
    from importlib.metadata import version as _version

    __version__ = _version("depende")
except Exception:
    __version__ = "0.0.0"
