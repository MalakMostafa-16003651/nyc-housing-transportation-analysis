"""Execute offline research/integration notebooks in an isolated temporary copy.

Run: python scripts/check_notebooks.py
Install requirements-analysis.txt first. Live-source housing cleaning and the
missing transportation cleaning notebook are outside this offline check.
"""
import json
from pathlib import Path
import shutil
import sys
import tempfile

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ["Person1_Research_Questions.ipynb", "Person2_Research_Questions.ipynb",
             "dataEngP3.ipynb", "RQ7_RQ8_Research_Questions.ipynb",
             "Person5_Research_Questions.ipynb"]


def main():
    with tempfile.TemporaryDirectory(prefix="nyc-notebooks-") as directory:
        work = Path(directory)
        kernel = work / "kernels" / "nyc"
        kernel.mkdir(parents=True)
        (kernel / "kernel.json").write_text(json.dumps({
            "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
            "display_name": "NYC analysis", "language": "python",
            "env": {"MPLCONFIGDIR": str(work / "matplotlib"),
                    "IPYTHONDIR": str(work / "ipython")},
        }))
        for csv in ROOT.glob("*.csv"):
            shutil.copy2(csv, work / csv.name)
        shutil.copytree(ROOT / "app", work / "app")
        for name in NOTEBOOKS:
            notebook = nbformat.read(ROOT / name, as_version=4)
            manager = KernelManager(kernel_name="nyc", kernel_spec_manager=
                                    KernelSpecManager(kernel_dirs=[str(work / "kernels")]))
            try:
                NotebookClient(notebook, km=manager, timeout=180,
                               resources={"metadata": {"path": str(work)}}).execute()
            finally:
                if manager.has_kernel:
                    manager.shutdown_kernel(now=True)
            executed = sum(c.cell_type == "code" and c.execution_count is not None
                           for c in notebook.cells)
            print(f"PASS {name}: {executed} code cells", flush=True)


if __name__ == "__main__":
    main()
