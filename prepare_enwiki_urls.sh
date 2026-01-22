#!/usr/bin/env bash

set -euo pipefail

ASSETS_DIR="$(pwd)/assets"

mkdir -p $ASSETS_DIR/datasets/quality_identifier

ENWIKI_URLS_GZ="$ASSETS_DIR/datasets/quality_identifier/enwiki-urls.txt.gz"
ENWIKI_URLS_TXT="${ENWIKI_URLS_GZ%.gz}"

if [ ! -f "$ENWIKI_URLS_TXT" ]; then
    echo "Downloading Enwiki URLs..."
    wget -c "https://nlp.stanford.edu/data/nfliu/cs336-spring-2024/assignment4/enwiki-20240420-extracted_urls.txt.gz" \
        -O "$ENWIKI_URLS_GZ"

    echo "Decompressing..."
    gzip -dk "$ENWIKI_URLS_GZ"
else
    echo "Enwiki URLs already exists, skipping download."
fi
