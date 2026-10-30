#!/usr/bin/env bash
# Preserve project history with git subtree split. Never delete source repositories.
# Requires git, gh CLI, Python 3. Run from a trusted Mac terminal.
set -euo pipefail
OWNER="7777Anne"
SOURCE="https://github.com/${OWNER}/Data-Science.git"
MODE="${1:---dry-run}"
if [[ "$MODE" != "--dry-run" && "$MODE" != "--execute" ]]; then
  echo "Usage: bash scripts/migrate_to_standalone_repos.sh [--dry-run|--execute]" >&2; exit 2
fi
command -v git >/dev/null || { echo "git required" >&2; exit 1; }
command -v gh >/dev/null || { echo "GitHub CLI (gh) required" >&2; exit 1; }
command -v python3 >/dev/null || { echo "Python 3 required" >&2; exit 1; }
if [[ "$MODE" == "--execute" ]]; then gh auth status || exit 1; fi

# Only the five implemented projects are promoted to standalone repositories.
# The existing hotel repo is already standalone and is not duplicated.
projects=(
  "fraud-risk-intelligence:fraud-risk-intelligence"
  "retail-demand-forecasting:retail-demand-forecasting"
  "revenue-forecasting:multi-series-revenue-forecasting"
  "transaction-lakehouse:transaction-lakehouse-pyspark"
  "industrial-knowledge-assistant:industrial-rag-assistant"
)
WORKDIR="$(mktemp -d)"
trap 'echo "Migration workspace: $WORKDIR (left intact for inspection)"' EXIT
echo "Source: $SOURCE"
echo "Mode: $MODE"
if [[ "$MODE" == "--dry-run" ]]; then
  for item in "${projects[@]}"; do
    IFS=: read -r src dst <<< "$item"
    echo "WOULD split projects/$src with git subtree and create $OWNER/$dst"
    echo "WOULD add root-level CI, standalone README paths and .gitignore"
  done
  echo "WOULD create $OWNER/$OWNER profile repository from templates/profile/README.md"
  echo "No GitHub changes made."
  exit 0
fi
git clone --quiet "$SOURCE" "$WORKDIR/source"
cd "$WORKDIR/source"
git fetch --quiet origin main
git checkout --quiet main
for item in "${projects[@]}"; do
  IFS=: read -r src dst <<< "$item"
  echo "Migrating $src -> $OWNER/$dst"
  # Fail rather than overwriting any existing destination repository.
  if gh repo view "$OWNER/$dst" >/dev/null 2>&1; then
    echo "Destination already exists: $OWNER/$dst. Stopping to avoid overwrites." >&2
    exit 1
  fi
  split_ref="migration-${src}"
  git subtree split --prefix="projects/$src" -b "$split_ref" >/dev/null
  split_sha="$(git rev-parse "$split_ref")"
  gh repo create "$OWNER/$dst" --public --description "Reproducible $src portfolio project: documented prototype and tests" || exit 1
  git push "https://github.com/$OWNER/$dst.git" "$split_sha:refs/heads/main"
  git clone --quiet "https://github.com/$OWNER/$dst.git" "$WORKDIR/$dst"
  (
    cd "$WORKDIR/$dst"
    python3 "$WORKDIR/source/scripts/prepare_standalone_project.py" "$src"
    git add README.md .gitignore .github
    if ! git diff --cached --quiet; then
      git commit -m "Adapt project documentation and CI for standalone repository"
      git push origin main
    fi
  )
  echo "CREATED https://github.com/$OWNER/$dst"
done
if gh repo view "$OWNER/$OWNER" >/dev/null 2>&1; then
  echo "Profile repository already exists. Not overwriting. Update README manually." >&2
else
  gh repo create "$OWNER/$OWNER" --public --description "GitHub profile README for applied ML and data engineering portfolio"
  git clone --quiet "https://github.com/$OWNER/$OWNER.git" "$WORKDIR/profile"
  cp "$WORKDIR/source/templates/profile/README.md" "$WORKDIR/profile/README.md"
  (
    cd "$WORKDIR/profile"
    git checkout -b main
    git add README.md
    git commit -m "Create recruiter-facing GitHub profile README"
    git push origin main
  )
fi
echo "Done. Verify CI and repository links before pinning repositories on profile."
