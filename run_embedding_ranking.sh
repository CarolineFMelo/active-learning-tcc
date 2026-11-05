#!/usr/bin/env bash
#
# Creates/reuses a virtual environment, installs the required
# dependencies and runs the embedding-based similarity ranking
# across all images in the training split.
#
# Usage:
#   ./run_embedding_ranking.sh
#
set -euo pipefail

# Directory where this script lives (works from anywhere)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

VENV_DIR="${SCRIPT_DIR}/.venv"
EMBED_SCRIPT="${SCRIPT_DIR}/embedding_ranking.py"

# ------------------------------------------------------------
# 1) Create the virtual environment (only if it doesn't exist)
# ------------------------------------------------------------

if [ ! -d "${VENV_DIR}" ]; then
    echo "==> Creating virtual environment at ${VENV_DIR}"
    python3 -m venv "${VENV_DIR}"
else
    echo "==> Reusing existing virtual environment at ${VENV_DIR}"
fi

# ------------------------------------------------------------
# 2) Activate the venv
# ------------------------------------------------------------

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

# ------------------------------------------------------------
# 3) Install/upgrade dependencies
# ------------------------------------------------------------

echo "==> Upgrading pip"
python -m pip install --upgrade pip

echo "==> Installing dependencies (torch, transformers, pillow, numpy, pyyaml, matplotlib)"
# transformers loads DINOv2 (facebook/dinov2-base)
# torch may already come from a previous ultralytics install
python -m pip install --upgrade \
    torch \
    transformers \
    pillow \
    numpy \
    pyyaml \
    matplotlib

# ------------------------------------------------------------
# 4) Run the embedding-based ranking
# ------------------------------------------------------------

echo "==> Starting the embedding-based similarity ranking (DINOv2)"
python "${EMBED_SCRIPT}"

echo "==> Done."
