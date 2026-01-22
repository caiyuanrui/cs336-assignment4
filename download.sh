#!/usr/bin/env bash

set -euo pipefail

ASSETS_DIR="$(pwd)/assets"

mkdir -p "$ASSETS_DIR/warcs"
mkdir -p "$ASSETS_DIR/models"

aws s3 cp \
    s3://commoncrawl/crawl-data/CC-MAIN-2025-18/segments/1744889135610.12/warc/CC-MAIN-20250417135010-20250417165010-00065.warc.gz \
    "$ASSETS_DIR/warcs" \
    --no-overwrite

aws s3 cp \
    s3://commoncrawl/crawl-data/CC-MAIN-2025-18/segments/1744889135610.12/wet/CC-MAIN-20250417135010-20250417165010-00065.warc.wet.gz \
    "$ASSETS_DIR/warcs" \
    --no-overwrite

wget -nc https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin -O "$ASSETS_DIR/models/lid.176.bin"

wget -nc "https://huggingface.co/allenai/dolma-jigsaw-fasttext-bigrams-nsfw/resolve/main/model.bin" \
    -O "$ASSETS_DIR/models/dolma_fasttext_nsfw_jigsaw_model.bin"

wget -nc "https://huggingface.co/allenai/dolma-jigsaw-fasttext-bigrams-hatespeech/resolve/main/model.bin" \
    -O "$ASSETS_DIR/models/dolma_fasttext_hatespeech_jigsaw_model.bin"
