"""Adapt a subtree-split project to repository-root paths, tests, and CI.

Usage: python prepare_standalone_project.py <original-project-slug>
Run from the destination repository root. No GitHub credentials required.
"""
from __future__ import annotations
import sys
from pathlib import Path

PROJECTS = {
    "fraud-risk-intelligence": ("python src/pipeline.py", "pytest -q tests"),
    "retail-demand-forecasting": ("python pipeline.py\n          python plot_results.py", "pytest -q tests"),
    "revenue-forecasting": ("python pipeline.py\n          python plot_results.py", "pytest -q tests"),
    "transaction-lakehouse": ("python src/pipeline.py", "pytest -q tests"),
    "industrial-knowledge-assistant": ("python evaluate.py", "pytest -q tests"),
}

def main(slug: str) -> None:
    if slug not in PROJECTS:
        raise ValueError(f"Unknown project {slug!r}")
    root = Path.cwd()
    if not (root / "README.md").is_file():
        raise FileNotFoundError("Run from a standalone project repository root")
    readme = root / "README.md"
    text = readme.read_text(encoding="utf-8")
    # Rewrite monorepo invocation paths to repository-root paths.
    text = text.replace(f"projects/{slug}/", "")
    text = text.replace("../../docs/DATASET_REGISTER.md", "https://github.com/7777Anne/Data-Science/blob/main/docs/DATASET_REGISTER.md")
    text = text.replace("docs/DATA_CARD.md", "docs/DATA_CARD.md")
    readme.write_text(text, encoding="utf-8")
    ignore = root / ".gitignore"
    original = ignore.read_text(encoding="utf-8") if ignore.exists() else ""
    additions = """
# Generated artifacts, secrets, caches, and raw datasets
.venv/
__pycache__/
.pytest_cache/
.ruff_cache/
.mypy_cache/
.env
.env.*
!.env.example
outputs/
artifacts/*
!artifacts/.gitkeep
data/raw/*
!data/raw/.gitkeep
*.joblib
*.pkl
*.parquet
.DS_Store
"""
    ignore.write_text(original + "\n" + additions, encoding="utf-8")
    run, tests = PROJECTS[slug]
    workflow = f"""name: standalone-project-ci
on:
  push:
    branches: [main]
  pull_request:
jobs:
  unit-and-demo:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: python -m pip install -r requirements.txt
      - name: Unit tests
        run: {tests}
      - name: Run reproducible demo
        run: |
          {run}
"""
    path = root / ".github" / "workflows" / "ci.yml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(workflow, encoding="utf-8")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python prepare_standalone_project.py <slug>")
    main(sys.argv[1])
