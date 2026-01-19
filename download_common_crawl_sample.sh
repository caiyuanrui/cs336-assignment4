#!/bin/env bash

set -euo pipefail

aws s3 cp \
  s3://commoncrawl/crawl-data/CC-MAIN-2025-18/segments/1744889135610.12/warc/CC-MAIN-20250417135010-20250417165010-00065.warc.gz \
  ./data \
  --no-overwrite

aws s3 cp \
  s3://commoncrawl/crawl-data/CC-MAIN-2025-18/segments/1744889135610.12/wet/CC-MAIN-20250417135010-20250417165010-00065.warc.wet.gz \
  ./data \
  --no-overwrite
