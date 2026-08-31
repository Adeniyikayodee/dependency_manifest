# Reproduce the claims in the README from scratch, with nothing to install.
#
#   docker build -t derives-from .
#   docker run --rm derives-from                    # the linter, offline
#   docker run --rm derives-from python reproduce_svi.py   # needs network
#
# The linter itself needs no network, which you can hold it to:
#   docker run --rm --network none derives-from
FROM python:3.13-slim

# curl backs the download fallback in reproduce_svi.py. urllib succeeds on Linux,
# so this path is unused here, but shipping the script without it would leave a
# documented code path quietly unavailable.
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /work

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copied file by file on purpose. A blanket COPY . would bake the working notes
# and the source PDF into an image that is meant to be shareable.
COPY derivation-manifest.yaml lint_lineage.py reproduce_svi.py ./

CMD ["python", "lint_lineage.py"]
