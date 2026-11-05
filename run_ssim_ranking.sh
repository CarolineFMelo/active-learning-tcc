#!/usr/bin/env bash
#
# Creates/reuses a virtual environment, installs the required
# dependencies and runs the SSIM similarity ranking script
# across all images in the training split.
#
# Usage:
#   ./run_ssim_ranking.sh
#
set -euo pipefail

# Directory where this script lives (works from anywhere)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

VENV_DIR="${SCRIPT_DIR}/.venv"
SSIM_SCRIPT="${SCRIPT_DIR}/ssim_ranking.py"

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

echo "==> Installing dependencies (opencv, scikit-image, numpy, pyyaml, matplotlib)"
python -m pip install --upgrade \
    opencv-python-headless \
    scikit-image \
    numpy \
    pyyaml \
    matplotlib

# ------------------------------------------------------------
# 4) Run the SSIM ranking
# ------------------------------------------------------------

echo "==> Starting the SSIM similarity ranking"
python "${SSIM_SCRIPT}"

echo "==> Done."
