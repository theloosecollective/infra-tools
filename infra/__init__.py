# Allow "import infra.deploys" to resolve to top-level "deploys"
import sys, importlib
for _name in ("deploys", "facts", "operations"):
    sys.modules[f"infra.{_name}"] = importlib.import_module(_name)
