"""Execute every notebook from archived raw inputs in an isolated copy.

Run: python scripts/check_notebooks.py
Install requirements-analysis.txt first. --write-executed updates notebook outputs
and the four README PNGs only after every notebook succeeds. CSVs remain isolated.
"""
import argparse
import hashlib
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
NOTEBOOKS = ["Housing_Data_Cleaning.ipynb", "Transport_Data_Cleaning.ipynb",
             "dataEngP3.ipynb", "Person1_Research_Questions.ipynb", "Person2_Research_Questions.ipynb",
             "RQ7_RQ8_Research_Questions.ipynb",
             "Person5_Research_Questions.ipynb"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-executed", action="store_true")
    parser.add_argument("--notebooks", nargs="+", choices=NOTEBOOKS, default=NOTEBOOKS,
                        help="Run a selected subset; default executes all seven notebooks.")
    parser.add_argument("--output-directory", type=Path,
                        help="Optionally retain generated tables/HTML outside the checkout data.")
    args = parser.parse_args()
    manifest = json.loads((ROOT / "data/raw/manifest.json").read_text(encoding="utf-8"))
    for source in manifest["sources"]:
        path = ROOT / "data/raw" / source["file"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            raise ValueError(f"Archived source hash differs: {path.name}")
    print("PASS archived raw source SHA-256 checks", flush=True)
    # Keep temporary writes within the selected checkout, including on restricted
    # Windows sessions where the OS temporary directory is not writable.
    with tempfile.TemporaryDirectory(prefix=".nyc-notebooks-", dir=ROOT) as directory:
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
        for folder in ["app", "scripts", "data"]:
            shutil.copytree(ROOT / folder, work / folder,
                            ignore=shutil.ignore_patterns("__pycache__"))
        results = {}
        for name in args.notebooks:
            print(f"RUN {name}", flush=True)
            notebook = nbformat.read(ROOT / name, as_version=4)
            manager = KernelManager(kernel_name="nyc", kernel_spec_manager=
                                    KernelSpecManager(kernel_dirs=[str(work / "kernels")]),
                                    connection_file=str(work / (Path(name).stem + "-kernel.json")))
            try:
                NotebookClient(notebook, km=manager, timeout=180, startup_timeout=60,
                               resources={"metadata": {"path": str(work)}}).execute()
            finally:
                if manager.has_kernel:
                    manager.shutdown_kernel(now=True)
            executed = sum(c.cell_type == "code" and c.execution_count is not None
                           for c in notebook.cells)
            print(f"PASS {name}: {executed} code cells", flush=True)
            results[name] = notebook
        if args.write_executed:
            for name, notebook in results.items():
                nbformat.write(notebook, ROOT / name)
            figures = 0
            for name in ["rq1_housing_vs_crashes_scatter.png", "rq2_borough_grouped_bar.png",
                         "rq7_buildings_vs_severe_injuries_scatter.png", "rq8_crashes_per_project_bar.png"]:
                if (work / name).is_file():
                    shutil.copy2(work / name, ROOT / name)
                    figures += 1
            print(f"Updated executed notebooks and {figures} README figures; source/cleaned CSVs unchanged.", flush=True)
        if args.output_directory:
            target = args.output_directory.resolve()
            target.mkdir(parents=True, exist_ok=True)
            for name, notebook in results.items():
                nbformat.write(notebook, target / name)
            if (work / "outputs").exists():
                shutil.copytree(work / "outputs", target / "outputs", dirs_exist_ok=True)
            print(f"Retained verification outputs: {target}", flush=True)


if __name__ == "__main__":
    main()
